from django.apps import AppConfig


class Config(AppConfig):
    name = 'bitcaster'

    def ready(self):
        from .config.environ import env  # noqa
        from . import celery  # noqa
        from django.conf import settings  # noqa
        from .dispatchers.registry import dispatcher_registry  # noqa
        from . import tasks  # noqa
        from . import checks  # noqa
        from . import handlers  # noqa
