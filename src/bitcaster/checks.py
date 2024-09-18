from typing import Any

from django.apps import AppConfig
from django.conf import settings
from django.core.checks import CheckMessage, Error, register
from django.utils.module_loading import import_string

from bitcaster.config import env

E001 = Error(
    "'%s' is not a valid function fully qualified name" % env("AGENT_FILESYSTEM_VALIDATOR"),
    id="settings_testing.E001",
)


@register("config")
def check_agent_validator(app_configs: AppConfig, **kwargs: Any) -> list[CheckMessage]:
    if not callable(settings.AGENT_FILESYSTEM_VALIDATOR):
        try:
            import_string(env("AGENT_FILESYSTEM_VALIDATOR"))
        except ImportError:
            return [E001]
        return []
