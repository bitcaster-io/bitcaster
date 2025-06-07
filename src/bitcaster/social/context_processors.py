from typing import TYPE_CHECKING

from bitcaster.social.models import SocialProvider

if TYPE_CHECKING:
    from django.http import HttpRequest


def available_providers(request: "HttpRequest") -> dict[str, list[tuple[str, str]]]:
    return {"sso_providers": SocialProvider.objects.choices()}
