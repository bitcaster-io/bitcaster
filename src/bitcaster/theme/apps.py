from django.apps import AppConfig


class Config(AppConfig):
    verbose_name = "Bitcaster Theme"
    name = "bitcaster.theme"
    default_auto_field = "django.db.models.BigAutoField"
    default_site = "bitcaster.theme.admin_site.BitcasterAdminSite"


class AdminConfig(AppConfig):
    verbose_name = "Admin"
    name = "bitcaster.theme.admin"
    # module = "bitcaster.admin"
    default_auto_field = "django.db.models.BigAutoField"
    default_site = "bitcaster.admin_site.BitcasterAdminSite"

    def ready(self) -> None:
        from bitcaster.admin import register  # noqa
