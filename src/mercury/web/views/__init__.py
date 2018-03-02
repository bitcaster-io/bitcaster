# -*- coding: utf-8 -*-
"""
mercury / __init__.py
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from .base import MercuryTemplateView  # noqa
from .login_logout import LoginView, LogoutView  # noqa
from .register import RegistrationForm, UserRegister, confirm_email  # noqa
from .user import UserProfileView  # noqa
from .views import (ApplicationDetail, ChannelList, EventList,  # noqa
                    MessageList, OrganizationDetail, SubscriptionList,)
