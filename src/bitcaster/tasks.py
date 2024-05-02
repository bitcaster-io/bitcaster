import logging

from bitcaster.config.celery import app
from bitcaster.constants import SystemEvent
from bitcaster.state import state

logger = logging.getLogger(__name__)


@app.task()
def process_event(occurrence_pk: int) -> None:

    from bitcaster.models import Occurrence

    o: Occurrence = Occurrence.objects.select_related("event").select_for_update().get(id=occurrence_pk)
    if o.attempts > 0:
        o.attempts = o.attempts - 1
        o.save()
        if o.status == Occurrence.Status.NEW:
            try:
                o.process()
                o.status = Occurrence.Status.PROCESSED
                o.recipients = len(o.data.get("delivered", []))
                o.save()
                if o.recipients == 0:
                    state.app.events.get(name=SystemEvent.OCCURRENCE_SILENCE.value).trigger(o.context, o.correlation_id)
            except Exception as e:
                logger.exception(e)
    elif o.attempts == 0 and o.status == Occurrence.Status.NEW:
        o.status = Occurrence.Status.FAILED
        o.save()
        state.app.events.get(name=SystemEvent.OCCURRENCE_ERROR.value).trigger(o.context, o.correlation_id)
