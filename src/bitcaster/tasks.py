import logging

from django.db import transaction

from bitcaster.config.celery import app
from bitcaster.constants import Bitcaster, SystemEvent

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
                        Bitcaster.trigger_event(
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
                Bitcaster.trigger_event(
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
