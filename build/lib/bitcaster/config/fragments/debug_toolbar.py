import sys
from typing import TYPE_CHECKING

from django_regex.utils import RegexList

if TYPE_CHECKING:
    from bitcaster.types.http import AuthHttpRequest


def show_ddt(request: "AuthHttpRequest") -> bool:  # pragma: no-cover
    from flags.state import flag_enabled

    if request.path in RegexList(("/api/.*", "/dal/.*", "/healthcheck/", "/webpush/")):
        return False
    return flag_enabled("DEVELOP_DEBUG_TOOLBAR", request=request)


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_ddt,
    "JQUERY_URL": "",
    "IS_RUNNING_TESTS": lambda: "pytest" in sys.argv,
    "EXTRA_SIGNALS": [],
    "DISABLE_PANELS": [
        "debug_toolbar.panels.profiling.ProfilingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
    ],
}
DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    "debug_toolbar.panels.profiling.ProfilingPanel",
    "flags.panels.FlagsPanel",
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.history.HistoryPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.redirects.RedirectsPanel",
]
