import os

import celery
from celery.apps.worker import Worker
from celery.signals import celeryd_after_setup
from django.conf import settings

from bitcaster.config.environ import env
from bitcaster.state import state


class BitcasterCelery(celery.Celery):
    task_cls = 'bitcaster.celery:BitcasterTask'


# class TaskRouter:
#     def route_for_task(self, task, *args, **kwargs):
#         if ':' not in task:
#             return {'queue': 'celery'}
#         namespace, _ = task.split(':')
#         return {'queue': namespace}


class BitcasterTask(celery.Task):

    def apply_async(self, args=None, kwargs=None, task_id=None, producer=None, link=None, link_error=None, shadow=None,
                    **options):
        return super().apply_async(args, kwargs, task_id, producer, link, link_error, shadow, **options)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bitcaster.config.settings')

app = BitcasterCelery('bitcaster',
                      loglevel='error',
                      broker=env.str('CELERY_BROKER_URL'))
app.config_from_object('django.conf:settings', namespace='CELERY', force=True)

app.conf.ONCE = {
    'backend': 'celery_once.backends.Redis',
    'settings': {
        'url': settings.CACHES['lock']['LOCATION'],
        'default_timeout': 60 * 60
    }
}

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.autodiscover_tasks(lambda: ['bitcaster'])


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@celeryd_after_setup.connect
def setup_state(instance: Worker, conf, **kwargs):
    from bitcaster.models import Organization
    state.data['organization'] = Organization.objects.first()
