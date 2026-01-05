from django.apps import AppConfig


class Config(AppConfig):
    verbose_name = "Chrome plugin"
    name = "bitcaster.chrome"

    def ready(self) -> None:
        pass
