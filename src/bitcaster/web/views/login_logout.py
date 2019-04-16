# -*- coding: utf-8 -*-
import logging

from django.contrib.auth.views import (LoginView as _LoginView,
                                       LogoutView as _LogoutView,)

from bitcaster.web.forms.user import AuthenticationForm

logger = logging.getLogger(__name__)


class LogoutView(_LogoutView):
    next_page = 'login'


class LoginView(_LoginView):
    form_class = AuthenticationForm
    template_name = 'bitcaster/login.html'

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Login'
        return super().get_context_data(**kwargs)
