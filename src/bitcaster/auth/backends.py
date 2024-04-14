from typing import TYPE_CHECKING, Any, Optional

from bitcaster.models import User

if TYPE_CHECKING:
    from bitcaster.types.http import AnyRequest


class BitcasterBackend:
    def authenticate(
        self, request: "AnyRequest", username: Optional[str] = None, password: Optional[str] = None, **kwargs: Any
    ) -> Optional[User]:
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            return None
        if password and user.check_password(password):
            return user
        return None
