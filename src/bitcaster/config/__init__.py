from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Tuple, TypeAlias, Union

from environ import Env

if TYPE_CHECKING:
    ConfigItem: TypeAlias = Union[Tuple[type, Any, str, Any], Tuple[type, Any, str], Tuple[type, Any]]


DJANGO_HELP_BASE = "https://docs.djangoproject.com/en/5.0/ref/settings"


def setting(anchor: str) -> str:
    return f"@see {DJANGO_HELP_BASE}#{anchor}"


class Group(Enum):
    DJANGO = 1


NOT_SET = "<- not set ->"
EXPLICIT_SET = ["DATABASE_URL", "SECRET_KEY"]

CONFIG: "Dict[str, ConfigItem]" = {
    "ADMIN_EMAIL": (str, "", "Initial user created at first deploy"),
    "ADMIN_PASSWORD": (str, "", "Password for initial user created at first deploy"),
    "ALLOWED_HOSTS": (list, ["127.0.0.1", "localhost"], setting("allowed-hosts")),
    "AUTHENTICATION_BACKENDS": (list, [], setting("authentication-backends")),
    "CACHE_URL": (str, "redis://localhost:6379/0"),
    "CATCH_ALL_EMAIL": (str, "If set all the emails will be sent to this address"),
    "CELERY_BROKER_URL": (str, NOT_SET, "https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html"),
    "CELERY_TASK_ALWAYS_EAGER": (
        bool,
        False,
        "https://docs.celeryq.dev/en/stable/userguide/configuration.html#std-setting-task_always_eager",
        True,
    ),
    "CELERY_TASK_EAGER_PROPAGATES": (
        bool,
        True,
        "https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-eager-propagates",
    ),
    "CELERY_VISIBILITY_TIMEOUT": (
        int,
        1800,
        "https://docs.celeryq.dev/en/stable/userguide/configuration.html#broker-transport-options",
    ),
    "CSRF_COOKIE_SECURE": (bool, True, setting("csrf-cookie-secure")),
    "DATABASE_URL": (
        str,
        "sqlite:///bitcaster.db",
        "https://django-environ.readthedocs.io/en/latest/types.html#environ-env-db-url",
        "",
    ),
    "DEBUG": (bool, False, setting("debug"), True),
    # "EMAIL_BACKEND": (str, "anymail.backends.mailjet.EmailBackend", "Do not change in prod"),
    # "EMAIL_HOST": (str, ""),
    # "EMAIL_HOST_PASSWORD": (str, ""),
    # "EMAIL_HOST_USER": (str, ""),
    # "EMAIL_PORT": (str, ""),
    # "EMAIL_USE_SSL": (str, ""),
    # "EMAIL_USE_TLS": (str, ""),
    "LOGGING_LEVEL": (str, "CRITICAL", setting("logging-level")),
    "MEDIA_FILE_STORAGE": (str, "django.core.files.storage.FileSystemStorage", setting("storages")),
    "MEDIA_ROOT": (str, "/tmp/media/", setting("media-root")),
    "MEDIA_URL": (str, "/media/", setting("media-url")),
    "SECRET_KEY": (str, NOT_SET, setting("secret-key")),
    "SECURE_HSTS_PRELOAD": (bool, True, setting("secure-hsts-preload"), False),
    "SECURE_HSTS_SECONDS": (int, 60, setting("secure-hsts-seconds")),
    "SECURE_SSL_REDIRECT": (bool, True, setting("secure-ssl-redirect"), False),
    "SENTRY_DSN": (str, "", "Sentry DSN"),
    "SENTRY_ENVIRONMENT": (str, "production", "Sentry Environment"),
    "SENTRY_URL": (str, "", "Sentry server url"),
    "SESSION_COOKIE_DOMAIN": (str, "bitcaster.org", setting("std-setting-SESSION_COOKIE_DOMAIN"), 1),
    "SESSION_COOKIE_HTTPONLY": (bool, True, setting("session-cookie-httponly")),
    "SESSION_COOKIE_NAME": (str, "bitcaster_session", setting("session-cookie-name")),
    "SESSION_COOKIE_PATH": (str, "/", setting("session-cookie-path")),
    "SESSION_COOKIE_SECURE": (bool, True, setting("session-cookie-secure"), False),
    "SIGNING_BACKEND": (str, "django.core.signing.TimestampSigner", setting("signing-backend")),
    "SOCIAL_AUTH_REDIRECT_IS_HTTPS": (
        bool,
        True,
        "https://python-social-auth.readthedocs.io/en/latest/configuration/settings.html",
        False,
    ),
    "STATIC_FILE_STORAGE": (str, "django.core.files.storage.FileSystemStorage", setting("storages")),
    "STATIC_ROOT": (str, "/tmp/static/", setting("static-root")),
    "STATIC_URL": (str, "/static/", setting("static-url")),
    "TIME_ZONE": (str, "UTC", setting("std-setting-TIME_ZONE")),
}


class SmartEnv(Env):
    def __init__(self, **scheme):  # type: ignore[no-untyped-def]
        self.raw = scheme
        values = {k: v[:2] for k, v in scheme.items()}
        super().__init__(**values)

    def get_help(self, key: str) -> str:
        entry: "ConfigItem" = self.raw.get(key, "")
        if len(entry) > 2:
            return entry[2]
        return ""

    def for_develop(self, key: str) -> Any:
        entry: ConfigItem = self.raw.get(key, "")
        if len(entry) > 3:
            return entry[3]
        return self.get_value(key)

    def get_default(self, var: str) -> Any:
        var_name = f"{self.prefix}{var}"
        if var_name in self.scheme:
            var_info = self.scheme[var_name]

            if len(var_info) > 1:
                value = var_info[1]
                cast = var_info[0]
            else:
                cast = var_info
                value = ""

            prefix = b"$" if isinstance(value, bytes) else "$"
            escape = rb"\$" if isinstance(value, bytes) else r"\$"
            if hasattr(value, "startswith") and value.startswith(prefix):
                value = value.lstrip(prefix)
                value = self.get_value(value, cast=cast)

            if self.escape_proxy and hasattr(value, "replace"):
                value = value.replace(escape, prefix)

        return value


env = SmartEnv(**CONFIG)  # type: ignore[no-untyped-call]
