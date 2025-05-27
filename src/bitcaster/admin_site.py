import contextlib
from datetime import timedelta
from typing import Any

from django.contrib.admin import apps
from django.contrib.admin.sites import AdminSite
from django.db.models import F, Model
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy
from flags.state import flag_enabled

from bitcaster.cache.storage import qs_get_or_store
from bitcaster.constants import CacheKey


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

        structure: list[tuple[type[Model], str]] = []
        if org := m.Organization.objects.local().first():
            org_url = org.get_admin_change()
            structure.append((m.Organization, org_url))
        else:
            org_url = m.Organization.get_admin_add()
            structure.append((m.Organization, org_url))
            return {"structure": structure}

        if prj := m.Project.objects.local().first():
            prj_url = prj.get_admin_change()
            structure.append((m.Project, prj_url))
        else:
            prj_url = f"{m.Project.get_admin_add()}?organization={org.pk}"
            structure.append((m.Project, prj_url))
            return {"structure": structure}

        return {
            "system": [
                # (m.Organization, org_url),
                # (m.Project, prj_url),
                m.Channel,
                m.DistributionList,
                m.Application,
                m.Event,
                m.Message,
                m.MediaFile,
                m.Monitor,
                # m.Notification,
                # m.Address,
                # m.Assignment,
            ],
            "configuration": [FlagState, Config, m.SocialProvider],
            "security": [m.User, auth_models.Group, m.UserRole, auth_models.Permission, m.ApiKey],
            "structure": structure,
        }

    def _build_sections_dict(self, request: HttpRequest) -> dict[str, Any]:
        sections = self._get_sections()
        app_dict = {}

        for section_name, models in sections.items():
            for model in models:
                admin_url = None
                if isinstance(model, tuple | list):
                    model, admin_url = model  # noqa: PLW2901
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
                    "admin_url": admin_url,
                }
                if admin_url is None and (perms.get("change") or perms.get("view")):
                    model_dict["view_only"] = not perms.get("change")
                    with contextlib.suppress(NoReverseMatch):
                        model_dict["admin_url"] = reverse("admin:%s_%s_changelist" % info, current_app=self.name)

                if section_name in app_dict:
                    app_dict[section_name]["models"].append(model_dict)
                else:
                    app_dict[section_name] = {
                        "name": section_name,
                        # "name": apps.get_app_config(app_label).verbose_name,
                        "app_label": section_name,
                        # "app_url": "#",
                        # "has_module_perms": has_module_perms,
                        "models": [model_dict],
                    }

        # for __, app in app_dict.items():
        #     app["models"].sort(key=lambda x: x["name"])

        return app_dict

    def get_app_list(self, request: HttpRequest, app_label: str | None = None) -> list[str]:
        if flag_enabled("OLD_STYLE_UI"):
            return super().get_app_list(request, app_label)
        return list(self._build_sections_dict(request).values())

    def get_last_events(self) -> list[dict[str, Any]]:
        from bitcaster.models import Occurrence

        offset = timezone.now() - timedelta(hours=24)
        qs = (
            Occurrence.objects.filter(timestamp__gte=offset)
            .values("timestamp", "id", application=F("event__application__name"), event__name=F("event__name"))
            .order_by("-timestamp")
        )
        return qs_get_or_store(qs, key=CacheKey.DASHBOARDS_EVENTS)  # type: ignore[arg-type]

    def each_context(self, request: HttpRequest) -> dict[str, Any]:
        ret = super().each_context(request)
        ret["django_ui"] = flag_enabled("OLD_STYLE_UI")
        return ret

    def index(self, request: HttpRequest, extra_context: dict[str, Any] | None = None) -> TemplateResponse:
        django_ui = flag_enabled("OLD_STYLE_UI")
        extra_context = {"django_ui": django_ui}
        if not django_ui:
            extra_context.update(
                {
                    "sections": list(self._build_sections_dict(request).values()),
                    "last_events": self.get_last_events(),
                }
            )

        return super().index(request, extra_context)
