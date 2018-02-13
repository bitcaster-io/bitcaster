# -*- coding: utf-8 -*-
from django.contrib.auth.models import Group, Permission

from .admin import *  # noqa
from .site import site  # noqa

site.register(Group)
site.register(Permission)
