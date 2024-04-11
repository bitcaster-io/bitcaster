from django.apps import AppConfig
from django.contrib import admin
from django.utils.translation import gettext_lazy


class BitcasterAdminSite(admin.AdminSite):
    site_title = gettext_lazy("Bitcaster site admin")
    site_header = gettext_lazy("Bitcaster administration")
    index_title = gettext_lazy("Site administration")
    site_url = "/"


class AdminConfig(AppConfig):
    verbose_name = "Admin"
    name = "bitcaster.admin"
    default_auto_field = "django.db.models.BigAutoField"
    default_site = "bitcaster.admin_site.BitcasterAdminSite"

    def ready(self) -> None:
        from bitcaster.admin import register  # noqa
