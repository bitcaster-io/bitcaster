import os
from pathlib import Path
from typing import Any

from django.apps import AppConfig
from django.conf import settings
from django.core.checks import CheckMessage, Error, register
from django.utils.module_loading import import_string

from bitcaster.config import env

E001 = Error(
    "'%s' is not a valid function fully qualified name" % env("AGENT_FILESYSTEM_VALIDATOR"),
    id="bitcaster.E001",
)

E002 = Error(
    "'%s' is not a valid directory" % env("AGENT_FILESYSTEM_ROOT"),
    hint="update AGENT_FILESYSTEM_ROOT anv var",
    id="bitcaster.E002",
)

E003 = Error(
    "AGENT_FILESYSTEM_ROOT must be an absolute path to a directory",
    hint="update AGENT_FILESYSTEM_ROOT anv var",
    id="bitcaster.E003",
)


@register("config")
def check_agent_validator(app_configs: AppConfig, **kwargs: Any) -> list[CheckMessage]:
    if not callable(settings.AGENT_FILESYSTEM_VALIDATOR):
        try:
            import_string(env("AGENT_FILESYSTEM_VALIDATOR"))
        except ImportError:
            return [E001]
        return []
    return []


@register("config")
def check_agent_validator_root(app_configs: AppConfig, **kwargs: Any) -> list[CheckMessage]:
    if settings.AGENT_FILESYSTEM_ROOT:
        if not os.path.isabs(settings.AGENT_FILESYSTEM_ROOT):
            return [E003]
        if not Path(str(settings.AGENT_FILESYSTEM_ROOT)).is_dir():
            return [E002]
    return []
