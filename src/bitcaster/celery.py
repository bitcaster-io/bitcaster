import celery
from django.conf import settings


class BitcasterCelery(celery.Celery):
    pass
    # task_cls = 'bitcaster.celery:BitcasterTask'
    # log_cls = 'celery.app.log:Logging'


class BitcasterTask(celery.Task):
    pass


if not settings.configured:
    settings.configure()
app = BitcasterCelery('bitcaster',
                      loglevel='info',
                      broker='redis://localhost:6379')
# app.config_from_object('django.conf:settings', namespace='CELERY', force=True)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
# from bitcaster import tasks


#
#
# # app.log.setup()
#
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
