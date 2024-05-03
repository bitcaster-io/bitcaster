import logging

from bitcaster.config.celery import app
from bitcaster.constants import SystemEvent
from bitcaster.state import state

logger = logging.getLogger(__name__)


@app.task()
def process_event(occurrence_pk: int) -> int:

    from bitcaster.models import Occurrence

    try:
        o: Occurrence = Occurrence.objects.select_related("event").select_for_update().get(id=occurrence_pk)
        if o.attempts > 0:
            o.attempts = o.attempts - 1
            o.save()
            if o.status == Occurrence.Status.NEW:
                o.process()
                o.status = Occurrence.Status.PROCESSED
                o.recipients = len(o.data.get("delivered", []))
                o.save()
                if o.recipients == 0:
                    state.app.trigger_event(SystemEvent.OCCURRENCE_SILENCE.value, o.context, o.correlation_id)
                return o.recipients
        elif o.attempts == 0 and o.status == Occurrence.Status.NEW:
            o.status = Occurrence.Status.FAILED
            o.save()
            state.app.trigger_event(SystemEvent.OCCURRENCE_ERROR.value, o.context, o.correlation_id)
            return 0
    except Exception as e:
        logger.exception(e)
        raise e
