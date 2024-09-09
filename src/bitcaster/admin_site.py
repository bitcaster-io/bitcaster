from typing import Any, Optional

from django.contrib.admin import apps
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.urls import NoReverseMatch, reverse
from django.utils.text import capfirst
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

    def _get_sections(self) -> dict[str, Any]:
        from constance.admin import Config
        from django.contrib.auth import models as auth_models
        from flags.models import FlagState

        from bitcaster import models as m

        return {
            "system": [
                m.Event,
                m.Project,
                m.Application,
                m.Message,
                m.MediaFile,
                m.Notification,
                m.DistributionList,
                m.Organization,
                m.Channel,
            ],
            "configuration": [FlagState, Config, m.SocialProvider],
            "security": [m.User, auth_models.Group, m.UserRole, auth_models.Permission],
        }

    def _build_sections_dict(self, request: HttpRequest) -> dict[str, Any]:

        sections = self._get_sections()
        app_dict = {}

        for section_name, models in sections.items():
            for model in models:
                if model not in self._registry:
                    continue
                model_admin = self._registry[model]
                app_label = model._meta.app_label
                info = (app_label, model._meta.model_name)
                perms = model_admin.get_model_perms(request)
                model_dict = {
                    "model": model,
                    "name": capfirst(model._meta.verbose_name_plural),
                    "object_name": model._meta.object_name,
                    "perms": perms,
                    "admin_url": None,
                    "add_url": None,
                }
                if perms.get("change") or perms.get("view"):
                    model_dict["view_only"] = not perms.get("change")
                    try:
                        model_dict["admin_url"] = reverse("admin:%s_%s_changelist" % info, current_app=self.name)
                    except NoReverseMatch:  # pragma: no cover
                        pass  # nosec
                if perms.get("add"):
                    try:
                        model_dict["add_url"] = reverse("admin:%s_%s_add" % info, current_app=self.name)
                    except NoReverseMatch:  # pragma: no cover
                        pass  # nosec
                if section_name in app_dict:
                    app_dict[section_name]["models"].append(model_dict)
                else:
                    app_dict[section_name] = {
                        "name": section_name,
                        # "name": apps.get_app_config(app_label).verbose_name,
                        "app_label": section_name,
                        "app_url": "#",
                        # "has_module_perms": has_module_perms,
                        "models": [model_dict],
                    }

        for __, app in app_dict.items():
            app["models"].sort(key=lambda x: x["name"])

        return app_dict

    def index(self, request: HttpRequest, extra_context: Optional[dict[str, Any]] = None) -> TemplateResponse:
        if not flag_enabled("OLD_STYLE_UI"):
            extra_context = {"sections": list(self._build_sections_dict(request).values())}

        return super().index(request, extra_context)
