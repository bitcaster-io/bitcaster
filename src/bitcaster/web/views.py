from django.contrib import messages
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.forms import Form
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.urls import reverse_lazy


def index(request: "HttpRequest") -> TemplateResponse:
    return TemplateResponse(request, "bitcaster/index.html", {})


class LogoutView(BaseLogoutView):

    def get_success_url(self) -> str:
        return "/"


class LoginView(BaseLoginView):
    redirect_authenticated_user = True

    def get_success_url(self) -> str:
        return reverse_lazy("home")

    def form_invalid(self, form: "Form") -> HttpResponse:
        messages.error(self.request, "Invalid username or password")
        return self.render_to_response(self.get_context_data(form=form))
