from typing import TYPE_CHECKING

from django.contrib.admin import register
from django.template import RequestContext

from ..admin.address import Address, AddressAdmin
from ..admin.base import BitcasterModelAdmin
from ..admin.channel import ChannelAdmin
from ..admin.organization import OrganizationAdmin
from ..admin.project import ProjectAdmin
from ..admin.user import User, UserAdmin
from ..config.urls import console

if TYPE_CHECKING:
    from admin_extra_buttons.types import HandlerWithButton


class ConsoleAdminMixin(BitcasterModelAdmin):
    pass


@register(Address, site=console)
class AddressConsole(ConsoleAdminMixin, AddressAdmin):
    pass


@register(User, site=console)
class UserConsole(UserAdmin):
    def get_changeform_buttons(self, context: RequestContext) -> "list[HandlerWithButton]":
        return []

    def get_changelist_buttons(self, context: RequestContext) -> "list[HandlerWithButton]":
        return []
        # return [h for h in self.extra_button_handlers.values() if h.change_list in {True, None}]


# @register(Channel, site=console)
class ChannelConsole(ChannelAdmin):
    pass


# @register(Organization, site=console)
class OrganizationConsole(OrganizationAdmin):
    pass


# @register(Project, site=console)
class ProjectConsole(ProjectAdmin):
    pass
