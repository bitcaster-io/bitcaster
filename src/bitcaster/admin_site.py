# import contextlib
# from datetime import timedelta
# from typing import Any
#
from typing import Any

from django.contrib.admin.apps import AdminConfig
from django.apps import apps
from django.http import HttpRequest
from django.urls import reverse, NoReverseMatch
from django.utils.module_loading import autodiscover_modules
from django.utils.text import capfirst

# from django.contrib.admin.sites import AdminSite
# from django.db.models import F, Model
# from django.http import HttpRequest
# from django.template.response import TemplateResponse
# from django.urls import NoReverseMatch, reverse
# from django.utils import timezone
# from django.utils.text import capfirst
from django.utils.translation import gettext_lazy

# from flags.state import flag_enabled
#
# from bitcaster.cache.storage import qs_get_or_store
# from bitcaster.constants import CacheKey
from unfold.sites import UnfoldAdminSite


class BitcasterAdminConfig(AdminConfig):
    default_site = "bitcaster.admin_site.BitcasterAdminSite"


class AAAA(UnfoldAdminSite):
    def _build_app_dict(self, request, label=None):
        """
        Build the app dictionary. The optional `label` parameter filters models
        of a specific app.
        """
        app_dict = {}

        if label:
            models = {
                m: m_a
                for m, m_a in self._registry.items()
                if m._meta.app_label == label
            }
        else:
            models = self._registry

        for model, model_admin in models.items():
            app_label = model._meta.app_label

            has_module_perms = model_admin.has_module_permission(request)
            if not has_module_perms:
                continue

            perms = model_admin.get_model_perms(request)

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            if True not in perms.values():
                continue

            info = (app_label, model._meta.model_name)
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
                    model_dict["admin_url"] = reverse(
                        "%s:%s_%s_changelist" % (self.name, *info), current_app=self.name
                    )
                except NoReverseMatch:
                    pass
            if perms.get("add"):
                try:
                    model_dict["add_url"] = reverse(
                        "%s:%s_%s_add" % (self.name, *info), current_app=self.name
                    )
                except NoReverseMatch:
                    pass

            if app_label in app_dict:
                app_dict[app_label]["models"].append(model_dict)
            else:
                app_dict[app_label] = {
                    "name": apps.get_app_config(app_label).verbose_name,
                    "app_label": app_label,
                    "app_url": reverse(
                        "%s:app_list" % self.name,
                        kwargs={"app_label": app_label},
                        current_app=self.name,
                    ),
                    "has_module_perms": has_module_perms,
                    "models": [model_dict],
                }

        return app_dict



class BitcasterAdminSite(AAAA, UnfoldAdminSite):
    site_title = gettext_lazy("Bitcaster admin")

    def each_context(self, request: HttpRequest) -> dict[str, Any]:
        context = super().each_context(request)
        context['current_app'] = self.name
        return context


class ConsoleAdminSite(AAAA, UnfoldAdminSite):
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
        context['current_app'] = self.name
        return context
