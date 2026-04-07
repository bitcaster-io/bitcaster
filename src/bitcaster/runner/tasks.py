import logging
from typing import TYPE_CHECKING

import dramatiq
from django.db.models import Q
from dramatiq.actor import Actor, P, R
from strategy_field.utils import fqn

from bitcaster.constants import bitcaster

from ..console.utils import get_users_to_notify, set_user_latest_notify_time
from ..dispatchers import UserMessageDispatcher
from ..models import Monitor
from .broker import broker

if TYPE_CHECKING:
    from ..models.occurrence import OccurrenceOptions

logger = logging.getLogger(__name__)

dramatiq.set_broker(broker)


class SmartActor(Actor[P, R]):
    pass


def beat_heartbeat() -> None:
    from .manager import BackgroundManager

    BackgroundManager().scheduler_ping()


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
        options: "OccurrenceOptions" = {"filters": {"include": [{"pk__in": users}], "exclude": []}}
        evt: Event = Event.objects.get(pk=event_pk)
        evt.trigger(context={}, options=options)
        for uid in users:
            set_user_latest_notify_time(uid)


@dramatiq.actor(actor_class=SmartActor, logging=True)
def scan_occurrences() -> list[int]:
    from bitcaster.models import Occurrence

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
    return ret


@dramatiq.actor(actor_class=SmartActor, logging=True)
def delete_expired_user_messages() -> None | Exception:
    from bitcaster.models import UserMessage

    UserMessage.objects.expired().delete()


@dramatiq.actor(actor_class=SmartActor, logging=True)
def purge_occurrences() -> None | Exception:
    from bitcaster.models import Occurrence

    try:
        batch_size = 10000
        queryset = Occurrence.objects.purgeable()
        while queryset.exists():
            ids = queryset.values_list("pk", flat=True)[:batch_size]
            Occurrence.objects.filter(pk__in=list(ids)).delete()
    except Exception as e:
        logger.exception(e)
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
        monitor: "Monitor" = Monitor.objects.get(pk=pk)
    except Monitor.DoesNotExist as e:
        logger.exception(e)
        raise

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
        raise
    finally:
        monitor.save()
