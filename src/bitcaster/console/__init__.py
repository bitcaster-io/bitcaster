from django.contrib.admin import register

from ..admin.address import Address, AddressAdmin
from ..admin.user import User, UserAdmin
from ..config.urls import console


@register(Address, site=console)
class AddressConsole(AddressAdmin):
    pass


@register(User, site=console)
class UserConsole(UserAdmin):
    pass
