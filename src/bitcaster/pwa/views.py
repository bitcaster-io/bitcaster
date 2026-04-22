import json
import logging
from typing import Any, cast

from django import forms
from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView as BaseLoginView,
)
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.templatetags.static import static
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView, TemplateView, UpdateView
from timezone_field import TimeZoneFormField

from bitcaster.console.views import UserConsoleIndexView
from bitcaster.models import User, UserMessage
from bitcaster.utils.http import absolute_reverse, get_server_url

logger = logging.getLogger(__name__)


class PwaUserPrefForm(forms.ModelForm[User]):
    timezone = TimeZoneFormField(
        widget=forms.Select(attrs={"class": "w-full p-3 border rounded-lg dark:bg-gray-700 dark:border-gray-600"})
    )

    class Meta:
        model = User
        fields = ("timezone", "date_format", "time_format")
        widgets = {
            "date_format": forms.Select(
                attrs={"class": "w-full p-3 border rounded-lg dark:bg-gray-700 dark:border-gray-600"}
            ),
            "time_format": forms.Select(
                attrs={"class": "w-full p-3 border rounded-lg dark:bg-gray-700 dark:border-gray-600"}
            ),
        }


class PwaLoginView(BaseLoginView):
    template_name = "pwa/login.html"
    redirect_authenticated_user = True

    def get_success_url(self) -> str:
        return absolute_reverse("pwa:index")

    def get_form(self, form_class: type[AuthenticationForm] | None = None) -> AuthenticationForm:
        form = super().get_form(form_class)
        for field in form.fields.values():
            field.widget.attrs.update({"class": "w-full p-3 border rounded-lg dark:bg-gray-700 dark:border-gray-600"})
        return form


class PwaLogoutView(LoginRequiredMixin, TemplateView):
    login_url = "pwa:login"
    template_name = "pwa/logout_confirm.html"

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        auth_logout(request)
        return redirect(absolute_reverse("pwa:login"))

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return {"request": self.request, **kwargs}


class PwaIndexView(UserConsoleIndexView):
    login_url = "pwa:login"
    template_name = "pwa/index.html"
    paginate_by = 25

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["details_url"] = "pwa:detail"
        return context


class PwaDetailView(LoginRequiredMixin, DetailView[UserMessage]):
    login_url = "pwa:login"
    template_name = "pwa/detail.html"
    model = UserMessage
    context_object_name = "message"

    def get_object(self, queryset: QuerySet[UserMessage] | None = None) -> UserMessage:
        obj = super().get_object(queryset)
        if not obj.read:
            obj.read = timezone.now()
            obj.save()
        return obj


class PwaPrefsView(LoginRequiredMixin, UpdateView[User, PwaUserPrefForm]):
    login_url = "pwa:login"
    template_name = "pwa/prefs.html"
    model = User
    form_class = PwaUserPrefForm
    success_url = "."

    def get_object(self, queryset: QuerySet[User] | None = None) -> User:
        return cast("User", self.request.user)


class PwaServiceWorker(TemplateView):
    content_type = "application/javascript"
    template_name = "pwa/serviceworker.js"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        kwargs["urls"] = json.dumps(["favicon.ico", static("bitcaster/images/logos/logo48.png")])
        return super().get_context_data(**kwargs)

    @method_decorator(never_cache)
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        response_kwargs["headers"] = {"Service-Worker-Allowed": "/"}
        return super().render_to_response(context, **response_kwargs)


@never_cache
def manifest(request: HttpRequest, secret: str | None = None) -> HttpResponse:
    context = {
        "host": get_server_url(),
        "start_url": absolute_reverse("pwa:index"),
        "home": absolute_reverse("pwa:index"),
        "secret": secret,
        "manifest": absolute_reverse("pwa:manifest"),
    }
    for setting_name in dir(settings):
        if setting_name.startswith("PWA_"):
            value = getattr(settings, setting_name)
            if setting_name in ["PWA_APP_ICONS", "PWA_APP_SPLASH_SCREEN"]:
                context[setting_name] = json.dumps(value)
            else:
                context[setting_name] = value

    return render(
        request,
        "pwa/manifest.json",
        context,
        content_type="application/manifest+json",
    )


def offline(request: HttpRequest) -> HttpResponse:
    return render(request, "pwa/offline.html")
