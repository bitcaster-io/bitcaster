import logging

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdmin_
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from bitcaster.models import Application, Organisation, Project, Role, Section, Sender, User

logger = logging.getLogger(__name__)


class UserAdmin(UserAdmin_):
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    list_filter = ("is_staff", "is_superuser", "groups")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)


class SenderAdmin(TreeAdmin):
    form = movenodeform_factory(Sender)


class RoleAdmin(admin.ModelAdmin[Role]):
    pass


class OrganisationAdmin(admin.ModelAdmin[Organisation]):
    list_display = ("name",)
    form = movenodeform_factory(Organisation)


class ProjectAdmin(admin.ModelAdmin[Project]):
    list_display = ("name",)
    # form = movenodeform_factory(Project)


class ApplicationAdmin(admin.ModelAdmin[Application]):
    list_display = ("name",)
    # form = movenodeform_factory(Application)


class SectionAdmin(admin.ModelAdmin[Section]):
    list_display = ("name",)
    # form = movenodeform_factory(Section)


admin.site.register(Sender, SenderAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Section, SectionAdmin)
