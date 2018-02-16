from __future__ import absolute_import

from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.signals import request_started
from django.db import IntegrityError
from django.dispatch import receiver

import geo.urls

urlpatterns = (
    url(r"", include(admin.site.urls)),
    url(r"geo/", include(geo.urls)),
)


# @receiver(request_started)
# def c(*args, **kwargs):
#     user, __ = User.objects.get_or_create(username="sax", email="")
#     user.is_staff = True
#     user.is_superuser = True
#     user.set_password("123")
#     user.save()
