from typing import TYPE_CHECKING, Any, cast

import logging

import dramatiq
from dramatiq.actor import Actor, P, R

from django.db.models import Q
from strategy_field.utils import fqn

from bitcaster.constants import bitcaster

from .broker import broker
from ..console.utils import get_users_to_notify, set_user_latest_notify_time
from ..dispatchers import UserMessageDispatcher
from ..models import Monitor

if TYPE_CHECKING:
    from ..models.occurrence import OccurrenceOptions, ProcessingData

logger = logging.getLogger(__name__)

dramatiq.set_broker(broker)


class SmartActor(Actor[P, R]):
    pass


@dramatiq.actor(actor_class=SmartActor)
def process_occurrence(occurrence_pk: int, return_value: bool = False) -> int | None:
    from bitcaster.models import Occurrence

    try:
        o: Occurrence = Occurrence.objects.select_related("event").get(id=occurrence_pk)
        logger.debug(f"Processing occurrence {o}")
        delivered = o.process()
        if return_value:
            return delivered
        return None
    except Occurrence.DoesNotExist:
        raise


process_occurrence.logging = True


@dramatiq.actor(actor_class=SmartActor)
def check_for_new_user_messages() -> None:
    from bitcaster.models import Channel, Event

    users = get_users_to_notify()
    if (
        users
        and (ch := Channel.objects.filter(dispatcher=fqn(UserMessageDispatcher)).first())
        and (event_pk := ch.config.get("event"))
    ):
        options: "OccurrenceOptions" = {"filters": {"include": [{"pk__in": cast("list[Any]", users)}], "exclude": []}}
        evt: Event = Event.objects.get(pk=event_pk)
        evt.trigger(context={}, options=options)
        for uid in users:
            set_user_latest_notify_time(uid)


@dramatiq.actor(actor_class=SmartActor, max_retries=0, logging=True)
def process_deliveries_page(page: int = 0) -> int:
    from constance import config

    from django.db import transaction
    from django.utils import timezone

    from bitcaster.models import Delivery, Occurrence

    due = Q(status__in=(Delivery.Status.PENDING, Delivery.Status.ERROR)) & (
        Q(next_attempt_at__isnull=True) | Q(next_attempt_at__lte=timezone.now())
    )
    page_size = config.DELIVERY_PAGE_SIZE
    processed = 0
    occurrences: dict[int, Occurrence] = {}
    counts: dict[int, int] = {}
    with transaction.atomic():
        deliveries = list(
            Delivery.objects.select_for_update(skip_locked=True)
            .filter(due)
            .select_related("occurrence__event", "assignment__address__user", "channel")
            .order_by("pk")[page * page_size : (page + 1) * page_size]
        )
        for delivery in deliveries:
            try:
                delivery.send()
            except Exception as e:
                logger.exception(e)
                delivery.mark_error(e)
            occurrences.setdefault(delivery.occurrence_id, delivery.occurrence)
            counts[delivery.occurrence_id] = counts.get(delivery.occurrence_id, 0) + 1
            processed += 1
        if occurrences:
            pending = (Delivery.Status.PENDING, Delivery.Status.ERROR)
            for oid, occurrence in occurrences.items():
                processing = cast("ProcessingData", occurrence.data.setdefault("processing", {"phase2_attempts": []}))
                attempts = processing.setdefault("phase2_attempts", [])
                attempts.append({"at": timezone.now().isoformat(), "processed": counts[oid]})
                if not Delivery.objects.filter(occurrence_id=oid, status__in=pending).exists():
                    processing["finished_at"] = timezone.now().isoformat()
                    occurrence.status = Occurrence.Status.COMPLETED
                occurrence.save(update_fields=["data", "status", "last_updated"])
    return processed


@dramatiq.actor(actor_class=SmartActor, logging=True)
def scan_occurrences() -> list[int]:
    from django.utils import timezone

    from bitcaster.models import Delivery, Occurrence

    logger.debug("Scan new occurrences")
    o: Occurrence
    ret = []
    for o in (
        Occurrence.objects.select_related("event")
        .filter(status=Occurrence.Status.NEW)
        .exclude(Q(event__paused=True) | Q(event__application__paused=True))
    ):
        process_occurrence.send(o.id)
        ret.append(o.id)

    pending = Delivery.objects.exclude(status__in=(Delivery.Status.DELIVERED, Delivery.Status.FAILURE)).values(
        "occurrence_id"
    )
    updated = 0
    for o in Occurrence.objects.filter(status=Occurrence.Status.PROCESSING).exclude(pk__in=pending):
        processing = o.data.setdefault("processing", {"phase2_attempts": []})
        processing["finished_at"] = timezone.now().isoformat()
        o.status = Occurrence.Status.COMPLETED
        o.save(update_fields=["data", "status", "last_updated"])
        updated += 1
    if updated:
        logger.info(f"Marked {updated} occurrences as COMPLETED")
    return ret


@dramatiq.actor(actor_class=SmartActor, logging=True)
def delete_expired_user_messages() -> None | Exception:
    from bitcaster.models import UserMessage

    UserMessage.objects.expired().delete()


@dramatiq.actor(actor_class=SmartActor, logging=True)
def purge_occurrences(max_batches: int = 100) -> None | Exception:
    from django.db import transaction

    from bitcaster.models import Occurrence

    logger.info("Starting occurrence purge")
    try:
        batch_size = 10000
        iteration = 0
        while iteration < max_batches:
            with transaction.atomic():
                # Order by PK for deterministic batching
                ids = list(Occurrence.objects.purgeable().order_by("pk").values_list("pk", flat=True)[:batch_size])

                if not ids:
                    break

                Occurrence.objects.filter(pk__in=ids).delete()
                iteration += 1
                logger.debug(f"Deleted batch {iteration}")
    except Exception as e:
        logger.exception("Failed to purge occurrences")
        return e


@dramatiq.actor(actor_class=SmartActor, max_retries=0)
def run_event_simulation(simulation_pk: int) -> None:
    from constance import config

    from bitcaster.models import EventSimulation, Occurrence

    try:
        simulation: EventSimulation = EventSimulation.objects.select_related("event").get(pk=simulation_pk)
    except EventSimulation.DoesNotExist:
        logger.warning("EventSimulation %s does not exist", simulation_pk)
        return
    try:
        limit = config.DEBUG_PREVIEW_RENDER_LIMIT if simulation.mode == EventSimulation.Mode.PARTIAL else None
        occurrence = Occurrence(event=simulation.event, context=simulation.context, options=simulation.options)
        _, data = occurrence.preview(simulation.mode, limit)
        simulation.save_deliveries(data)
    except Exception as e:
        logger.exception(e)
        EventSimulation.objects.filter(pk=simulation.pk, status=Occurrence.Status.NEW).update(
            data={"errors": [f"{e.__class__.__name__}: {str(e)}"]}, status=Occurrence.Status.FAILED
        )


@dramatiq.actor(actor_class=SmartActor, logging=True)
def purge_event_simulations(max_batches: int = 100) -> None | Exception:
    from django.db import transaction

    from bitcaster.models import EventSimulation

    logger.info("Starting event simulations purge")
    try:
        batch_size = 10000
        iteration = 0
        while iteration < max_batches:
            with transaction.atomic():
                # Order by PK for deterministic batching
                ids = list(EventSimulation.objects.purgeable().order_by("pk").values_list("pk", flat=True)[:batch_size])

                if not ids:
                    break

                EventSimulation.objects.filter(pk__in=ids).delete()
                iteration += 1
                logger.debug(f"Deleted batch {iteration}")
    except Exception as e:
        logger.exception("Failed to purge event simulations")
        return e


@dramatiq.actor(actor_class=SmartActor, logging=True)
def monitor_run() -> None:
    for monitor in Monitor.objects.filter(active=True):
        monitor_check.send(monitor.pk)


@dramatiq.actor(actor_class=SmartActor, logging=True)
def monitor_check(pk: int) -> str:
    from django.contrib.admin.models import LogEntry
    from django.contrib.contenttypes.models import ContentType

    try:
        monitor: "Monitor" = Monitor.objects.get(active=True, pk=pk)
    except Monitor.DoesNotExist as e:
        logger.exception(e)
        return "Monitor not found or deactivated"

    try:
        if monitor.active:
            LogEntry.objects.create(
                content_type=ContentType.objects.get_for_model(Monitor),
                object_id=monitor.pk,
                action_flag=100,
                user=bitcaster.system_user,
                object_repr=str(monitor),
                change_message="Monitor started",
            )
            monitor.agent.check()
            monitor.result = {"message": "Success", "changes": monitor.agent.changes_detected()}
            return "done"
        return "inactive"
    except Exception as e:
        logger.exception(e)
        monitor.active = False
        monitor.result = {"error": str(e)}
        LogEntry.objects.create(
            content_type=ContentType.objects.get_for_model(Monitor),
            object_id=monitor.pk,
            action_flag=200,
            user=bitcaster.system_user,
            object_repr=str(monitor),
            change_message=f"Monitor failed: {e}",
        )
        raise
    finally:
        monitor.save()
