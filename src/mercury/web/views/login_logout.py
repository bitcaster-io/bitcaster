# -*- coding: utf-8 -*-
"""
mercury / login_logout
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from django.contrib.auth.views import (LoginView as _LoginView,
                                       LogoutView as _LogoutView,)

logger = logging.getLogger(__name__)


class LogoutView(_LogoutView):
    next_page = 'login'


class LoginView(_LoginView):
    template_name = 'bitcaster/login.html'
