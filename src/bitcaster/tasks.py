import logging

import dramatiq
from apscheduler.schedulers.blocking import BlockingScheduler
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone

from bitcaster.constants import bitcaster

logger = logging.getLogger(__name__)
scheduler = BlockingScheduler()


@dramatiq.actor
def beat_heartbeat() -> None:
    cache.set(
        "celery:beat:alive",
        timezone.now().isoformat(),
        timeout=None,  # None means infinite timeout in Django cache
    )


@dramatiq.actor
def process_occurrence(occurrence_pk: int) -> int:
    from bitcaster.models import Occurrence

    o: Occurrence = Occurrence.objects.select_related("event").get(id=occurrence_pk)
    return o.process()


@dramatiq.actor
def scan_occurrences() -> None:
    from bitcaster.models import Occurrence

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
