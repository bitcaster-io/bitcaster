from typing import Any

from django.contrib.admin.apps import AdminConfig
from django.http import HttpRequest
from django.utils.translation import gettext_lazy
from unfold.sites import UnfoldAdminSite


class BitcasterAdminConfig(AdminConfig):
    default_site = "bitcaster.admin_site.BitcasterAdminSite"


class BitcasterAdminSite(UnfoldAdminSite):
    site_title = gettext_lazy("Bitcaster admin2222")
    default_site = "bitcaster.admin_site.BitcasterAdminSite"
    settings_name = "UNFOLD"

    def each_context(self, request: HttpRequest) -> dict[str, Any]:
        context = super().each_context(request)
        context["current_app"] = self.name
        return context
