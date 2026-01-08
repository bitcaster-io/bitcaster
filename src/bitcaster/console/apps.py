from django.apps import AppConfig


class Config(AppConfig):
    verbose_name = "Console"
    name = "bitcaster.console"

    def ready(self) -> None:
        pass
