from typing import Any

from constance import config
from django.contrib.auth.models import Group, User
from social_core.backends.base import BaseAuth
from social_core.exceptions import AuthForbidden
from social_core.pipeline.user import create_user as _create_user
from social_core.storage import UserProtocol
from social_core.strategy import BaseStrategy

from bitcaster.constants import AddressType
from bitcaster.models import Address


def create_user(
    strategy: BaseStrategy, details, backend: BaseAuth, user: UserProtocol | None = None, *args: Any, **kwargs: Any
) -> dict[str, Any]:
    if config.SOCIAL_AUTH_CREATE_USER:
        return _create_user(strategy, details, backend, user, *args, **kwargs)

    email = details.get("email")
    if email:
        from bitcaster.models import User

        if u := User.objects.filter(email=email).first():
            return {"user": u, "is_new": False}
        raise AuthForbidden(backend)
    raise AuthForbidden(backend)


def save_to_group(backend: BaseAuth, user: User | None = None, **kwargs: Any) -> dict[str, Any]:
    if user and kwargs.get("is_new"):
        grp = Group.objects.get(name=config.NEW_USER_DEFAULT_GROUP)
        user.groups.add(grp)
    return {}


def add_email_address(backend: BaseAuth, user: User | None = None, **kwargs: Any) -> dict[str, Any]:
    if user and kwargs.get("is_new"):
        Address.objects.get_or_create(user=user, name="email", type=AddressType.EMAIL, value=user.email)
    return {}
