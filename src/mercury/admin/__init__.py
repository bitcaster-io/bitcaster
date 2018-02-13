# -*- coding: utf-8 -*-
from django.contrib.auth.models import Group, Permission

from .site import site  # noqa
from .admin import *  # noqa


site.register(Group)
site.register(Permission)
