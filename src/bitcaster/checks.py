import os
from pathlib import Path
from typing import Any

from django.apps import AppConfig
from django.conf import settings
from django.core import checks
from django.utils.module_loading import import_string

from bitcaster.config import env

E001 = checks.Error(
    "'%s' is not a valid function fully qualified name" % env("AGENT_FILESYSTEM_VALIDATOR"),
    id="bitcaster.E001",
)

E002 = checks.Error(
    "'%s' is not a valid directory" % env("AGENT_FILESYSTEM_ROOT"),
    hint="update AGENT_FILESYSTEM_ROOT anv var",
    id="bitcaster.E002",
)

E003 = checks.Error(
    "AGENT_FILESYSTEM_ROOT must be an absolute path to a directory",
    hint="update AGENT_FILESYSTEM_ROOT anv var",
    id="bitcaster.E003",
)

W001 = checks.Warning(
    "SENTRY_DSN is set but sentry_sdk is not installed",
    id="bitcaster.W001",
)


@checks.register("config")
def check_sentry(app_configs: AppConfig, **kwargs: Any) -> list[checks.CheckMessage]:
    if settings.SENTRY_DSN:
        try:
            import sentry_sdk

            if sentry_sdk.get_client().dsn:
                sentry_sdk.capture_message("Bitcaster System Check")
            else:
                return [W001]
        except ImportError:
            return [W001]
    return []


@checks.register("config")
def check_agent_validator(app_configs: AppConfig, **kwargs: Any) -> list[checks.CheckMessage]:
    if not callable(settings.AGENT_FILESYSTEM_VALIDATOR):
        try:
            import_string(env("AGENT_FILESYSTEM_VALIDATOR"))
        except ImportError:
            return [E001]
        return []
    return []


@checks.register("config")
def check_agent_validator_root(app_configs: AppConfig, **kwargs: Any) -> list[checks.CheckMessage]:
    if settings.AGENT_FILESYSTEM_ROOT:
        if not os.path.isabs(settings.AGENT_FILESYSTEM_ROOT):
            return [E003]
        if not Path(str(settings.AGENT_FILESYSTEM_ROOT)).is_dir():
            return [E002]
    return []
