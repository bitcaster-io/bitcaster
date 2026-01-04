from typing import Any

from constance import config
from django.contrib.auth.models import Group, User
from social_core.backends.base import BaseAuth

from bitcaster.constants import AddressType
from bitcaster.models import Address


def save_to_group(backend: BaseAuth, user: User | None = None, **kwargs: Any) -> dict[str, Any]:
    if user and kwargs.get("is_new"):
        grp = Group.objects.get(name=config.NEW_USER_DEFAULT_GROUP)
        user.groups.add(grp)
    return {}


def add_email_address(backend: BaseAuth, user: User | None = None, **kwargs: Any) -> dict[str, Any]:
    if user and kwargs.get("is_new"):
        Address.objects.get_or_create(user=user, name="email", type=AddressType.EMAIL, value=user.email)
    return {}
