from typing import Any

from django.conf import settings
from flags.state import flag_enabled


def is_root(request: Any, *args: Any, **kwargs: Any) -> bool:
    return settings.DEBUG and flag_enabled("IS_ROOT", request=request)
