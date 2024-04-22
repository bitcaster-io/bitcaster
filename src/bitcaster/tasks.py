import logging

from bitcaster.config.celery import app

logger = logging.getLogger(__name__)


@app.task()
def process_event(pk: int) -> None:

    from bitcaster.models import Occurrence

    o: Occurrence = Occurrence.objects.select_related("event").select_for_update().get(id=pk)
    if not o.processed:
        try:
            o.process()
            o.processed = True
            o.save()
            print(1)
        except Exception as e:
            logger.exception(e)
