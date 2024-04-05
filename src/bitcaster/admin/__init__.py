from django.contrib import admin

from ..models import Application, Organization, Project, Role, User
from .auth import RoleAdmin, UserAdmin
from .org import ApplicationAdmin, OrganisationAdmin, ProjectAdmin

admin.site.register(Role, RoleAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Organization, OrganisationAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Application, ApplicationAdmin)
