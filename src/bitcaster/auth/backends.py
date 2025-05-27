from typing import Any

from django.contrib.auth.backends import ModelBackend
from django.http import HttpRequest

from bitcaster.models import User


class BitcasterBackend(ModelBackend):
    def authenticate(
        self, request: HttpRequest | None, username: str | None = None, password: str | None = None, **kwargs: Any
    ) -> User | None:
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            return None
        if password and user.check_password(password):
            return user
        return None
