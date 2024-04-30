from typing import Any, Optional

from constance import config
from django.contrib.auth.models import Group, User
from social_core.backends.base import BaseAuth


def save_to_group(backend: BaseAuth, user: Optional[User] = None, **kwargs: Any) -> dict[str, Any]:
    if user:
        grp = Group.objects.get(name=config.NEW_USER_DEFAULT_GROUP)
        user.groups.add(grp)
    return {}
