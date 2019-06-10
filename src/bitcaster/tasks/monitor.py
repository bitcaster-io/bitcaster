import logging

from crashlog.middleware import process_exception

from bitcaster.celery import app
from bitcaster.models.monitor import Monitor

logger = logging.getLogger(__name__)


@app.task()
def check_monitor(monitor_pk):
    monitor = Monitor.objects.filter(enabled=True).get(pk=monitor_pk)
    logger.info('Checking monitor %s' % monitor)
    try:
        return monitor.handler.poll()
    except Exception as e:
        logger.exception(e)
        from bitcaster.tsdb.api import log_monitor_error
        process_exception(e)
        log_monitor_error(monitor, 'Error polling')
        raise
