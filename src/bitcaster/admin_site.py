from typing import Any, Optional

from django.contrib.admin import apps
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy
from flags.state import flag_enabled


class BitcasterAdminConfig(apps.AdminConfig):
    default_site = "bitcaster.admin_site.BitcasterAdminSite"


class BitcasterAdminSite(AdminSite):
    site_title = gettext_lazy("Django site admin")
    site_header = gettext_lazy("Bitcaster")
    index_title = gettext_lazy("")
    site_url = "/"
    enable_nav_sidebar = False
    index_template = None

    def index(self, request: HttpRequest, extra_context: Optional[dict[str, Any]] = None) -> TemplateResponse:
        if flag_enabled("OLD_STYLE_UI"):
            self.index_template = None
        else:
            self.index_template = "admin/bc_index.html"

        return super().index(request, extra_context)
