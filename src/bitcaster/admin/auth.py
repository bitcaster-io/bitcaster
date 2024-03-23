from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdmin_
from bitcaster import models
from treebeard.admin import TreeAdmin


class UserAdmin(UserAdmin_):
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    list_filter = ("is_staff", "is_superuser", "groups")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)


class SenderAdmin(TreeAdmin):
    pass


class RoleAdmin(admin.ModelAdmin):
    pass


class OrganisationAdmin(admin.ModelAdmin):
    pass


class ApplicationAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Sender, SenderAdmin)
admin.site.register(models.Role, RoleAdmin)
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Organisation, OrganisationAdmin)
admin.site.register(models.Application, ApplicationAdmin)
