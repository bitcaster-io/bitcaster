# -*- coding: utf-8 -*-
# django-constance
from constance.admin import Config, ConstanceAdmin
from django.contrib.auth.models import Group, Permission

from .application import ApplicationAdmin  # noqa
from .channel import ChannelAdmin  # noqa
from .counters import CounterAdmin, LogEntryAdmin, OccurenceAdmin  # noqa
from .event import EventAdmin  # noqa
from .message import MessageAdmin  # noqa
from .security import ApiAuthTokenAdmin, ApiTriggerKeyAdmin, UserAdmin  # noqa
from .site import site  # noqa
from .subscription import SubscriptionAdmin  # noqa

site.register(Group)
site.register(Permission)

site.register([Config], ConstanceAdmin)
