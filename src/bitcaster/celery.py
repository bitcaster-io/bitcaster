import celery
from django.conf import settings

from bitcaster.config.environ import env


class BitcasterCelery(celery.Celery):
    task_cls = 'bitcaster.celery:BitcasterTask'


class BitcasterTask(celery.Task):

    def apply_async(self, args=None, kwargs=None, task_id=None, producer=None, link=None, link_error=None, shadow=None,
                    **options):
        return super().apply_async(args, kwargs, task_id, producer, link, link_error, shadow, **options)


if not settings.configured:
    settings.configure()

app = BitcasterCelery('bitcaster',
                      loglevel='info',
                      broker=env.str('CELERY_BROKER_URL'))
app.config_from_object('django.conf:settings', namespace='CELERY', force=True)
# app.config_from_object('bitcaster.config.settings',
#                        namespace='CELERY', force=True)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
