from django.apps import AppConfig


class Config(AppConfig):
    verbose_name = "Bitcaster"
    name = "bitcaster"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        from . import models
