import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from bitcaster.config.celery import app
from bitcaster.constants import SystemEvent, bitcaster
from bitcaster.models import LogEntry, User

logger = logging.getLogger(__name__)


@app.task()
def process_occurrence(occurrence_pk: int) -> int | Exception:
    from bitcaster.models import Occurrence

    try:
        with transaction.atomic():
            o: Occurrence = Occurrence.objects.select_related("event").select_for_update().get(id=occurrence_pk)
            if o.attempts > 0:
                o.attempts = o.attempts - 1
                o.save()
                if o.status == Occurrence.Status.NEW:
                    success = o.process()
                    if success:
                        o.status = Occurrence.Status.PROCESSED
                    o.recipients = len(o.data.get("delivered", []))
                    o.save()
                    if success and o.recipients == 0 and o.event.name != SystemEvent.OCCURRENCE_SILENCE.value:
                        bitcaster.trigger_event(
                            SystemEvent.OCCURRENCE_SILENCE,
                            o.context,
                            options=o.options,
                            correlation_id=o.correlation_id,
                            parent=o,
                        )
                    return o.recipients
            elif (
                o.attempts == 0
                and o.status == Occurrence.Status.NEW
                and o.event.name != SystemEvent.OCCURRENCE_SILENCE.value
            ):
                o.status = Occurrence.Status.FAILED
                o.save()
                bitcaster.trigger_event(
                    SystemEvent.OCCURRENCE_ERROR, options=o.options, correlation_id=o.correlation_id, parent=o
                )
                return 0
    except Exception as e:
        logger.exception(e)
        return e


@app.task()
def schedule_occurrences() -> None | Exception:
    from bitcaster.models import Occurrence

    o: Occurrence
    try:
        for o in Occurrence.objects.select_related("event").filter(status=Occurrence.Status.NEW):
            process_occurrence.delay(o.id)
    except Exception as e:
        logger.exception(e)
        return e


@app.task()
def purge_occurrences() -> None | Exception:
    from bitcaster.models import Occurrence

    try:
        Occurrence.objects.purgeable().delete()
    except Exception as e:
        logger.exception(e)
        return e


@app.task()
def monitor_run(pk: str) -> str:
    from django.contrib.contenttypes.models import ContentType

    from bitcaster.models import Monitor

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
                user=User.objects.get(username="__SYSTEM__"),
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
