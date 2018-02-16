# -*- coding: utf-8 -*-
from django.contrib.auth.models import Group, Permission

# django-constance
from constance.admin import Config, ConstanceAdmin

from .admin import *  # noqa
from .site import site  # noqa

site.register(Group)
site.register(Permission)

site.register([Config], ConstanceAdmin)
