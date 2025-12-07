import contextlib

from django.apps import apps
from django.urls import NoReverseMatch, reverse
from django.utils.text import capfirst
from unfold.sites import UnfoldAdminSite


class MultiAdminSite(UnfoldAdminSite):
    def _build_app_dict(self, request, label=None):
        # Override to reverse bases on site.name instead of hardcoded "admin:%s..."
        app_dict = {}

        if label:
            models = {m: m_a for m, m_a in self._registry.items() if m._meta.app_label == label}
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
                with contextlib.suppress(NoReverseMatch):
                    model_dict["admin_url"] = reverse("%s:%s_%s_changelist" % (self.name, *info), current_app=self.name)
            if perms.get("add"):
                with contextlib.suppress(NoReverseMatch):
                    model_dict["add_url"] = reverse("%s:%s_%s_add" % (self.name, *info), current_app=self.name)

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
