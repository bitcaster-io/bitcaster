from django.apps import AppConfig


class Config(AppConfig):
    verbose_name = "Bitcaster"
    name = "bitcaster"
    default_auto_field = "django.db.models.BigAutoField"

    # default_site = "bitcaster.admin.BitcasterAdminSite"

    def ready(self) -> None:
        from bitcaster.admin import register  # noqa

        from . import handlers  # noqa
