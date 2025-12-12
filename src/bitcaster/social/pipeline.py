from typing import Any

from constance import config
from django.contrib.auth.models import Group, User
from social_core.backends.base import BaseAuth


def save_to_group(backend: BaseAuth, user: User | None = None, **kwargs: Any) -> dict[str, Any]:
    if user and kwargs.get("created"):
        grp = Group.objects.get(name=config.NEW_USER_DEFAULT_GROUP)
        user.groups.add(grp)
    return {}
