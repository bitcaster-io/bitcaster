from django.apps import AppConfig


class Config(AppConfig):
    name = "bitcaster.help"
    verbose_name = "Help"

    def ready(self) -> None:
        from . import checks  # noqa
