import celery
from django.conf import settings


class MercuryCelery(celery.Celery):
    task_cls = 'mercury.celery:MercuryTask'
    log_cls = 'celery.app.log:Logging'


class MercuryTask(celery.Task):
    pass


app = MercuryCelery('mercury')
settings.CELERY_BROKER_URL = settings.CELERY_BROKER_URL
app.config_from_object('django.conf:settings', namespace='CELERY')
# WARN: autodiscover_tasks cannot be used because django-uwsgi.tasks
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.log.setup()
