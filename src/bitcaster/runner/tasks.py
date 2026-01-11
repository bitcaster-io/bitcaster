import logging
from typing import TYPE_CHECKING

import dramatiq
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from strategy_field.utils import fqn

from bitcaster.constants import bitcaster

from ..console.utils import get_users_to_notify, set_user_latest_notify_time
from ..dispatchers import UserMessageDispatcher
from .broker import broker

if TYPE_CHECKING:
    from ..models.occurrence import OccurrenceOptions

logger = logging.getLogger(__name__)

dramatiq.set_broker(broker)


def beat_heartbeat() -> None:
    from .manager import BackgroundManager

    BackgroundManager().scheduler_ping()


@dramatiq.actor
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


@dramatiq.actor
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


@dramatiq.actor
def scan_occurrences() -> None:
    from bitcaster.models import Occurrence

    logger.debug("Scan new occurrences")
    o: Occurrence
    try:
        for o in (
            Occurrence.objects.select_related("event")
            .filter(status=Occurrence.Status.NEW)
            .exclude(Q(event__paused=True) | Q(event__application__paused=True))
        ):
            process_occurrence.send(o.id)
    except Exception as e:
        logger.exception(e)
        raise


@dramatiq.actor
def delete_expired_user_messages() -> None | Exception:
    from bitcaster.models import UserMessage

    UserMessage.objects.expired().delete()


@dramatiq.actor
def purge_occurrences() -> None | Exception:
    from bitcaster.models import Occurrence

    try:
        Occurrence.objects.purgeable().delete()
    except Exception as e:
        logger.exception(e)
        return e


@dramatiq.actor
def monitor_run(pk: str) -> str:
    from django.contrib.contenttypes.models import ContentType

    from bitcaster.models import LogEntry, Monitor

    try:
        monitor: "Monitor" = Monitor.objects.get(pk=pk)
    except ObjectDoesNotExist as e:
        logger.exception(e)
        raise

    try:
        if monitor.active:
            LogEntry.objects.create(
                content_type=ContentType.objects.get_for_model(Monitor),
                object_id=pk,
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
