from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode

from django.http import HttpResponse
from social_core.backends.oauth import BaseOAuth2PKCE

if TYPE_CHECKING:
    from bitcaster.types.django import JsonType


class Wso2OAuth2(BaseOAuth2PKCE):
    """WSO2 OAuth authentication backend."""

    # https://python-social-auth.readthedocs.io/en/latest/backends/implementation.html

    name = "oauth2"
    ACCESS_TOKEN_METHOD = "POST"  # nosec  # noqa: S105
    SCOPE_SEPARATOR = ","
    EXTRA_DATA = [("id", "id"), ("expires", "expires")]
    REDIRECT_STATE = False
    DEFAULT_SCOPE = ["openid"]
    PKCE_DEFAULT_CODE_CHALLENGE_METHOD = "S256"
    PKCE_DEFAULT_CODE_VERIFIER_LENGTH = 100
    USER_FIELD_MAPPING = {
        "username": "sub",
        "email": "sub",
        "first_name": "given_name",
        "last_name": "family_name",
    }

    def authorization_url(self) -> str:
        return self.setting("AUTHORIZATION_URL")

    def access_token_url(self) -> str:
        return self.setting("ACCESS_TOKEN_URL")

    def userinfo_url(self) -> str:
        return self.setting("USERINFO_URL")

    def auth_url(self) -> str:
        """Return redirect url."""
        state = self.get_or_create_state()
        params = self.auth_params(state)
        params.update(self.get_scope_argument())
        params.update(self.auth_extra_arguments())
        params = urlencode(params)
        return f"{self.authorization_url()}?{params}"

    def auth_complete_params(self, state: str | None = None) -> dict[str, str]:
        ret = super().auth_complete_params(state)
        ret["code_challenge"] = self.get_code_verifier()
        ret["code_method"] = self.PKCE_DEFAULT_CODE_CHALLENGE_METHOD
        return ret

    def get_user_details(self, response: HttpResponse) -> dict[str, str]:
        """Return user details from WSO2 account."""
        base = self.setting("USER_FIELD_MAPPING", default=self.USER_FIELD_MAPPING)
        return {k: response.get(v) for k, v in base.items()}

    def user_data(self, access_token: str, *args: Any, **kwargs: Any) -> "JsonType":
        """Load user data from service."""
        url = f"{self.userinfo_url()}?" + urlencode({"access_token": access_token})
        return self.get_json(url)
