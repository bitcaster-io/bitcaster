from django.apps import AppConfig


class Config(AppConfig):
    name = "bitcaster.pwa"

    def ready(self):
        from . import handlers  # noqa
