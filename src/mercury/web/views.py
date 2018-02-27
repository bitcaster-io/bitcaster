from django.contrib.auth.views import (LoginView as _LoginView,
                                       LogoutView as _LogoutView,)
from django.views.generic import TemplateView


class LogoutView(_LogoutView):
    next_page = 'login'


class LoginView(_LoginView):
    template_name = 'bitcaster/login.html'


class HomeView(TemplateView):
    template_name = 'bitcaster/index.html'

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        return ret
