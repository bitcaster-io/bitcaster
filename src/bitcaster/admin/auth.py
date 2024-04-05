import logging

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdmin_

from bitcaster.models import Role

logger = logging.getLogger(__name__)


class UserAdmin(UserAdmin_):
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    list_filter = ("is_staff", "is_superuser", "groups")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)


class RoleAdmin(admin.ModelAdmin[Role]):
    pass
