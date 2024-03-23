import logging

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdmin_
from treebeard.admin import TreeAdmin

from bitcaster.models import Sender, User, Role, Organisation, Application, Section, Project

logger = logging.getLogger(__name__)


class UserAdmin(UserAdmin_):
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    list_filter = ("is_staff", "is_superuser", "groups")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)


class SenderAdmin(TreeAdmin[Sender]):
    pass


class RoleAdmin(admin.ModelAdmin[Role]):
    pass


class OrganisationAdmin(admin.ModelAdmin[Organisation]):
    pass


class ProjectAdmin(admin.ModelAdmin[Project]):
    pass


class ApplicationAdmin(admin.ModelAdmin[Application]):
    pass


class SectionAdmin(admin.ModelAdmin[Section]):
    pass


admin.site.register(Sender, SenderAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(Application, ApplicationAdmin)
