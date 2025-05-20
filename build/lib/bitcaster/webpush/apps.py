from django.apps import AppConfig


class Config(AppConfig):
    verbose_name = "WebPush"
    name = "bitcaster.webpush"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        from bitcaster.admin import register  # noqa

        from . import admin  # noqa
        from . import dispatcher  # noqa
