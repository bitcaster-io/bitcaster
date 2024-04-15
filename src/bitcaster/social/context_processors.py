from typing import List, Tuple

from django.http import HttpRequest

from bitcaster.social.models import SocialProvider


def available_providers(request: "HttpRequest") -> dict[str, List[Tuple[str, str]]]:
    return {"sso_providers": SocialProvider.objects.choices()}
