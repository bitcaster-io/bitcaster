from datetime import datetime
from typing import Any

from django import forms
from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.db.models import Model, QuerySet
from django.forms import HiddenInput
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic import TemplateView
from unfold.views import UnfoldModelAdminViewMixin

from bitcaster.cache.manager import CacheManager
from bitcaster.constants import bitcaster
from bitcaster.forms import unfold as uwidgets


class ConsoleMixin(UnfoldModelAdminViewMixin):
    pass


class ToolsView(ConsoleMixin, TemplateView):
    title = "Console: Tools"
    permission_required = ("bitcaster.console_tools",)
    template_name = "dashboards/tools.html"

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        cm = CacheManager(request)
        match request.POST.get("op"):
            case "clear_cache":
                cm.clear_cache()
                self.model_admin.message_user(request, "Cache cleared", messages.SUCCESS)
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        cm = CacheManager(self.request)
        ret = super().get_context_data(**kwargs)
        ret["opts"] = None
        ret["title"] = "console"
        ret.update({"cache_size": cm.count_keys()})
        return ret


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
    title = "Console: Lock"
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
        ret["title"] = "console"
        ret["action_title"] = "Lock"
        ret.update({"cache_size": cm.count_keys()})
        return ret


class MonitorView(ConsoleMixin, TemplateView):
    title = "Console: Monitor"
    permission_required = ("bitcaster.console_tools",)
    template_name = "dashboards/monitor.html"

    @property
    def media(self) -> forms.Media:
        extra = "" if settings.DEBUG else ".min"
        js = [
            "dashboards/monitor%s.js" % extra,
        ]
        css = {}
        return forms.Media(js=js, css=css)

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
