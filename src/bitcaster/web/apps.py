from django.apps import AppConfig


class Config(AppConfig):
    verbose_name = "Bitcaster Theme"
    name = "bitcaster.web"
    default_auto_field = "django.db.models.BigAutoField"
    default_site = "bitcaster.theme.admin_site.BitcasterAdminSite"
