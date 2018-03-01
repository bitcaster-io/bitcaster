# -*- coding: utf-8 -*-
"""
mercury / __init__.py
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from .base import MercuryTemplateView
from .register import RegistrationForm, UserRegister,confirm_email
from .views import ApplicationDetail, SubscriptionList, OrganizationDetail
from .login_logout import LoginView, LogoutView
from .user import UserProfile
