from typing import TYPE_CHECKING, Any

from datetime import datetime

from unfold.views import UnfoldModelAdminViewMixin

from django import forms
from django.apps import apps
from django.contrib import messages
from django.db.models import Model, QuerySet
from django.forms import HiddenInput
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from bitcaster.cache.manager import CacheManager
from bitcaster.constants import bitcaster
from bitcaster.forms import unfold as uwidgets
from bitcaster.utils.widgets import SmartMedia

if TYPE_CHECKING:
    from django.utils.functional import _StrPromise

SANITY_CATEGORIES = ("subscriptions", "distributionlists", "events")
SANITY_COMPONENT_ORDER = ("MessageTemplate", "Channel", "Event", "Application", "Project", "Notification")


class ConsoleMixin(UnfoldModelAdminViewMixin):
    def get_breadcrumbs(self) -> "tuple[tuple[str | _StrPromise, str], ...]":
        return (
            (reverse_lazy("admin:app_list", args=["bitcaster"]), "Bitcaster"),
            ("#", "Console"),
            (reverse_lazy(f"admin:console-{self.__class__.__name__.lower()}"), str(self.title)),
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        kwargs["breadcrumbs"] = self.get_breadcrumbs()
        return super().get_context_data(**kwargs)


def start_sanity_check(request: HttpRequest, model_admin: Any) -> None:
    from bitcaster.runner.tasks import sanity_check

    cm = CacheManager(request)
    cm.delete("sanity:subscriptions")
    cm.delete("sanity:distributionlists")
    cm.delete("sanity:events")
    cm.store("sanity:state", "scheduled", timeout=120, timeboxed=False)
    try:
        sanity_check.send()
    except Exception:
        cm.delete("sanity:state")
        raise
    model_admin.message_user(request, "Sanity check started", messages.SUCCESS)


class ToolsView(ConsoleMixin, TemplateView):
    title = "Tools"
    permission_required = ("bitcaster.console_tools",)
    template_name = "dashboards/tools.html"

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        cm = CacheManager(request)
        match request.POST.get("op"):
            case "clear_cache":
                cm.clear_cache()
                self.model_admin.message_user(request, "Cache cleared", messages.SUCCESS)
            case "run_sanity_check":
                start_sanity_check(request, self.model_admin)
            case _:
                self.model_admin.message_user(request, "Nothing selected", messages.WARNING)
        return redirect(request.path)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        cm = CacheManager(self.request)
        ret = super().get_context_data(**kwargs)
        ret["opts"] = None
        ret["title"] = "console"

        ret.update(
            {
                "cache_size": cm.count_keys(),
                "sanity_state": cm.retrieve("sanity:state") or "idle",
                "has_sanity_results": any(cm.retrieve(f"sanity:{key}") for key in SANITY_CATEGORIES),
            }
        )
        return ret


class SanityView(ConsoleMixin, TemplateView):
    title = "Sanity Check"
    permission_required = ("bitcaster.console_tools",)
    template_name = "dashboards/sanity.html"

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.POST.get("op") == "run_sanity_check":
            start_sanity_check(request, self.model_admin)
        return redirect(request.path)

    def get_breadcrumbs(self) -> "tuple[tuple[str | _StrPromise, str], ...]":
        return (
            (reverse_lazy("admin:app_list", args=["bitcaster"]), "Bitcaster"),
            ("#", "Console"),
            (reverse_lazy(f"admin:console-{ToolsView.__name__.lower()}"), str(ToolsView.title)),
            (reverse_lazy(f"admin:console-{self.__class__.__name__.lower()}"), str(self.title)),
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        cm = CacheManager(self.request)
        results: dict[str, Any] = {}
        components: dict[str, list[dict[str, str]]] = {}
        for key in SANITY_CATEGORIES:
            report = cm.retrieve(f"sanity:{key}")
            if report:
                results[key] = report
                for item in report.get("invalid", []):
                    components.setdefault(item["component"], []).append(item)
        grouped = {name: components[name] for name in SANITY_COMPONENT_ORDER if name in components}
        kwargs.update(
            {
                "results": results,
                "components": grouped,
                "has_results": bool(results),
                "sanity_state": cm.retrieve("sanity:state") or "idle",
            }
        )
        return super().get_context_data(**kwargs)


def form_builder(qs: QuerySet[Model], mode: str, data: dict[str, Any] | None = None) -> forms.Form:
    model = qs.model

    class FormClass(forms.Form):
        form_id = model._meta.model_name.lower()
        title = model._meta.verbose_name_plural
        model_name = forms.CharField(widget=HiddenInput)
        op = forms.CharField(widget=HiddenInput)
        target = forms.ModelChoiceField(label="", queryset=qs, widget=uwidgets.UnfoldAdminSelectWidget)

    return FormClass(data, initial={"model_name": f"{model._meta.app_label}.{model._meta.model_name}", "op": mode})


class LockView(ConsoleMixin, TemplateView):
    title = "Lock"
    permission_required = ("bitcaster.console_lock",)
    template_name = "dashboards/lock.html"
    targets: dict[str, dict[str, Any]] = {
        "bitcaster.application": {"project__organization__name": bitcaster.ORGANIZATION},
        "bitcaster.event": {"application__project__organization__name": bitcaster.ORGANIZATION},
        # "bitcaster.occurrence": {"event__application__project__organization__name": bitcaster.ORGANIZATION},
        # "bitcaster.user": {"is_staff": True},
    }

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        model_name: str = request.POST.get("model_name", "")
        op = request.POST.get("op", "")
        model = apps.get_model(*model_name.split("."))  # type: ignore[arg-type]
        qs = model.objects.exclude(**self.targets[model_name])
        form = form_builder(qs, op, request.POST)
        if form.is_valid():
            target = form.cleaned_data["target"]
            match op:
                case "lock":
                    target.lock()
                    self.model_admin.message_user(request, f"{target} locked", messages.SUCCESS)
                case "pause":
                    target.pause()
                    self.model_admin.message_user(request, f"{target} paused", messages.SUCCESS)
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        cm = CacheManager(self.request)
        ret = super().get_context_data(**kwargs)
        _forms = {"lock": [], "pause": []}
        for model_name, filters in self.targets.items():
            model = apps.get_model(*model_name.split("."))  # type: ignore[arg-type]
            qs = model.objects.exclude(**filters)
            _forms["lock"].append(form_builder(qs, "lock"))
            _forms["pause"].append(form_builder(qs, "pause"))

        ret["forms"] = _forms
        ret.update({"cache_size": cm.count_keys()})
        return ret


class MonitorView(ConsoleMixin, TemplateView):
    title = "Monitor"
    permission_required = ("bitcaster.console_tools",)
    template_name = "dashboards/monitor.html"

    @property
    def media(self) -> forms.Media:
        js = [
            "dashboards/monitor{min}.js",
        ]
        css = {}
        return SmartMedia(js=js, css=css)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        from bitcaster.runner.manager import BackgroundManager

        manager = BackgroundManager()
        return JsonResponse(
            {
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "beat": manager.scheduler_info(),
                "workers": manager.get_runners(),
            }
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        from bitcaster.runner.broker import broker
        from bitcaster.runner.manager import BackgroundManager

        manager = BackgroundManager()

        kwargs.update(
            media=self.media,
            tasks=[
                (a, manager.get_task_last_run(a)) for a in broker.get_declared_actors()
            ],  # Removed reference to app.tasks
        )

        return super().get_context_data(**kwargs)
