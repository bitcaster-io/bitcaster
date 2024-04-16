from typing import Any

from django.conf import settings


def is_root(request: Any, *args: Any, **kwargs: Any) -> bool:
    return request.user.is_superuser and request.headers.get(settings.ROOT_TOKEN_HEADER) == settings.ROOT_TOKEN != ""
