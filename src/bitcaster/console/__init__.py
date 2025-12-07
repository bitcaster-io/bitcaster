from django.contrib.admin import register

from ..admin.address import Address, AddressAdmin
from ..admin.channel import Channel, ChannelAdmin
from ..admin.organization import Organization, OrganizationAdmin
from ..admin.project import Project, ProjectAdmin
from ..admin.user import User, UserAdmin
from ..config.urls import console


@register(Address, site=console)
class AddressConsole(AddressAdmin):
    pass


@register(User, site=console)
class UserConsole(UserAdmin):
    pass


# @register(Channel, site=console)
class ChannelConsole(ChannelAdmin):
    pass


# @register(Organization, site=console)
class OrganizationConsole(OrganizationAdmin):
    pass


# @register(Project, site=console)
class ProjectConsole(ProjectAdmin):
    pass
