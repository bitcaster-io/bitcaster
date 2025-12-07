from typing import Any

from django.contrib.admin.apps import AdminConfig
from django.http import HttpRequest
from django.utils.module_loading import autodiscover_modules
from django.utils.translation import gettext_lazy
from unfold.sites import UnfoldAdminSite

from bitcaster.multi_admin.site import MultiAdminSite


class BitcasterAdminConfig(AdminConfig):
    default_site = "bitcaster.admin_site.BitcasterAdminSite"


class BitcasterAdminSite(MultiAdminSite, UnfoldAdminSite):
    site_title = gettext_lazy("Bitcaster admin")

    def each_context(self, request: HttpRequest) -> dict[str, Any]:
        context = super().each_context(request)
        context["current_app"] = self.name
        return context


class ConsoleAdminSite(MultiAdminSite, UnfoldAdminSite):
    site_title = gettext_lazy("Bitcaster console")
    default_site = "bitcaster.admin_site.ConsoleAdminSite"
    settings_name = "CONSOLE"

    def autodiscover(self):
        autodiscover_modules("console", register_to=self)

    def _build_app_dict(self, request, label=None):
        autodiscover_modules("console", register_to=self)
        return super()._build_app_dict(request, label)

    def each_context(self, request: HttpRequest) -> dict[str, Any]:
        context = super().each_context(request)
        context["current_app"] = self.name
        return context
