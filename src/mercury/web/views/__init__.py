# -*- coding: utf-8 -*-
"""
mercury / __init__.py
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from .application import *  # noqa
from .base import MercuryTemplateView  # noqa
from .login_logout import LoginView, LogoutView  # noqa
from .organization import *  # noqa
from .register import *  # noqa
from .settings import *  # noqa
from .system_setup import *  # noqa
from .user import *  # noqa
from .views import *  # noqa
from .callbacks import confirm_email  # noqa
