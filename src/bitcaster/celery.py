import celery
from django.conf import settings


class BitcasterCelery(celery.Celery):
    task_cls = 'bitcaster.celery:BitcasterTask'
    log_cls = 'celery.app.log:Logging'


class BitcasterTask(celery.Task):
    pass


app = BitcasterCelery('bitcaster')
settings.CELERY_BROKER_URL = settings.CELERY_BROKER_URL
app.config_from_object('django.conf:settings', namespace='CELERY')
# WARN: autodiscover_tasks cannot be used because django-uwsgi.tasks
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.log.setup()
