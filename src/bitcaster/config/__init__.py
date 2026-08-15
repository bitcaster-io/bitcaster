from typing import TYPE_CHECKING, Any, Mapping

from enum import Enum
from urllib import parse

from environ import Env

if TYPE_CHECKING:
    type ItemValue = str | bool | int | list[str] | None
    type ConfigItem = tuple[type, ItemValue] | tuple[type, ItemValue, str] | tuple[type, ItemValue, str, Any]


DJANGO_HELP_BASE = "https://docs.djangoproject.com/en/5.0/ref/settings"


def setting(anchor: str) -> str:
    return f"@see {DJANGO_HELP_BASE}#{anchor}"


class Group(Enum):
    DJANGO = 1


NOT_SET = "<- not set ->"
EXPLICIT_SET = ["DATABASE_URL", "SECRET_KEY", "CACHE_URL", "DRAMATIQ_BROKER", "MEDIA_ROOT", "STATIC_ROOT"]

CONFIG: "Mapping[str, ConfigItem]" = {
    "ADMIN_EMAIL": (str, "", "Initial user created at first deploy"),
    "ADMIN_PASSWORD": (str, "", "Password for initial user created at first deploy"),
    "AGENT_FILESYSTEM_VALIDATOR": (
        str,
        "bitcaster.agents.fs.validate_path",
        "Callable to validate agent filesystem path",
        None,
    ),
    "AGENT_FILESYSTEM_ROOT": (str, "", "AgentFilesystem root directory", ""),
    "AGENT_FILESYSTEM_DISALLOWED": (list, "", "AgentFilesystem disallowed directories"),
    "ALLOWED_HOSTS": (list, ["127.0.0.1", "localhost"], setting("allowed-hosts")),
    "AUTHENTICATION_BACKENDS": (list, [], setting("authentication-backends")),
    "BITCASTER_DOCUMENTATION_SITE_URL": (
        str,
        "https://docs.bitcaster.io",
        "Bitcaster documentation site. (no trailing slash)",
    ),
    "CACHE_PREFIX": (str, "", "", "prefix string to use in cache keys"),
    "CACHE_URL": (str, "redis://cache-server:6379/0", "", "redis://cache-server:6379/0"),
    "CHANNEL_SERVER": (str, "channel-server:6379", "", "channel-server:6379"),
    "CLIENT_TOKEN_TTL": (int, 900, "Lifetime in seconds of client tokens minted via the token exchange endpoint"),
    "CORS_ALLOWED_ORIGINS": (
        list,
        [],
        "Origins allowed to call the API from a browser (full origins, no trailing slash)",
    ),
    "CATCH_ALL_EMAIL": (str, "If set all the emails will be sent to this address"),
    "CSRF_COOKIE_SECURE": (bool, True, setting("csrf-cookie-secure"), False),
    "CSRF_COOKIE_SAMESITE": (str, setting("csrf-cookie-samesite")),
    "CSRF_TRUSTED_ORIGINS": (list, ["http://localhost", "http://127.0.0.1"]),
    "DATABASE_URL": (
        str,
        "sqlite:///bitcaster.db",
        "https://django-environ.readthedocs.io/en/latest/types.html#environ-env-db-url",
        False,
    ),
    "DRAMATIQ_BROKER": (str, "redis://dramatiq-broker:6379/0", "", "redis://dramatiq-broker:6379/0"),
    "DEBUG": (bool, False, setting("debug"), True),
    "EMAIL_BACKEND": (str, "django.core.mail.backends.smtp.EmailBackend", setting("email-backend"), True),
    "EMAIL_HOST": (str, "localhost", setting("email-host"), True),
    "EMAIL_HOST_USER": (str, "", setting("email-host-user"), True),
    "EMAIL_HOST_PASSWORD": (str, "", setting("email-host-password"), True),
    "EMAIL_PORT": (int, "25", setting("email-port"), True),
    "EMAIL_SUBJECT_PREFIX": (str, "[Bitcaster]", setting("email-subject-prefix"), True),
    "EMAIL_USE_LOCALTIME": (bool, False, setting("email-use-localtime"), True),
    "EMAIL_USE_TLS": (bool, False, setting("email-use-tls"), True),
    "EMAIL_USE_SSL": (bool, False, setting("email-use-ssl"), True),
    "EMAIL_TIMEOUT": (str, None, setting("email-timeout"), True),
    "ENVIRONMENT": (str, "production", "Bitcaster Environment", "local"),
    "EXTRA_APPS": (list, [], setting("configuring-applications")),
    "INTERNAL_IPS": (list, [], setting("internal-ips"), ["127.0.0.1", "localhost"]),
    "LOGGING_LEVEL": (str, "CRITICAL", setting("logging-level"), "DEBUG"),
    "MEDIA_FILE_STORAGE": (str, "django.core.files.storage.FileSystemStorage", setting("storages")),
    "MEDIA_ROOT": (str, None, setting("media-root")),
    "MEDIA_URL": (str, "/media/", setting("media-url")),
    "SECRET_KEY": (str, NOT_SET, setting("secret-key")),
    "SECURE_HSTS_PRELOAD": (bool, True, setting("secure-hsts-preload"), False),
    "SECURE_HSTS_SECONDS": (int, 60, setting("secure-hsts-seconds")),
    "SECURE_PROXY_SSL_HEADER": (tuple, "", setting("secure-proxy-ssl-header")),
    "SECURE_SSL_REDIRECT": (bool, True, setting("secure-ssl-redirect"), False),
    "SENTRY_DSN": (str, "", "Sentry DSN"),
    "SENTRY_ENVIRONMENT": (str, "production", "Sentry Environment"),
    "SENTRY_URL": (str, "", "Sentry server url"),
    "STORAGE_DEFAULT": (str, "django.core.files.storage.FileSystemStorage", setting("storages")),
    "STORAGE_MEDIA": (str, "", setting("storages")),
    "STORAGE_STATIC": (str, "django.contrib.staticfiles.storage.StaticFilesStorage", setting("storages")),
    "SESSION_COOKIE_DOMAIN": (str, "bitcaster.io", setting("std-setting-SESSION_COOKIE_DOMAIN"), False),
    "SESSION_COOKIE_HTTPONLY": (bool, True, setting("session-cookie-httponly"), False),
    "SESSION_COOKIE_NAME": (str, "bitcaster_session", setting("session-cookie-name")),
    "SESSION_COOKIE_PATH": (str, "/", setting("session-cookie-path")),
    "SESSION_COOKIE_SECURE": (bool, True, setting("session-cookie-secure"), False),
    "SIGNING_BACKEND": (str, "django.core.signing.TimestampSigner", setting("signing-backend")),
    "REDIRECT_TO_HTTPS": (
        bool,
        False,
        "",
        False,
    ),
    "STATIC_FILE_STORAGE": (str, "django.core.files.storage.FileSystemStorage", setting("storages")),
    "STATIC_ROOT": (str, "/var/bitcaster/static", setting("static-root")),
    "STATIC_URL": (str, "/static/", setting("static-url")),
    "SUPERUSERS": (list, [], "Users in this list will be granted superuser privileges when created."),
    "TIME_ZONE": (str, "UTC", setting("std-setting-TIME_ZONE")),
    "TRIGGER_CONTEXT_MAX_SIZE": (
        int,
        32768,
        "Maximum size in bytes of the serialized context payload accepted from web credentials",
    ),
    "USE_X_FORWARDED_HOST": (bool, False, setting("use-x-forwarded-host")),
    "USE_X_FORWARDED_PORT": (bool, False, setting("use-x-forwarded-port")),
}


# x
class SmartEnv(Env):
    def __init__(self, **scheme: "ConfigItem") -> None:
        self.raw: "dict[str, ConfigItem]" = scheme
        values = {k: v[:2] for k, v in scheme.items()}
        super().__init__(**values)

    def get_help(self, key: str) -> str:
        entry: "ConfigItem | str" = self.raw.get(key, "")
        if len(entry) > 2:
            return entry[2]
        return ""

    def for_develop(self, key: str) -> Any:
        entry: "ConfigItem | str" = self.raw.get(key, "")
        if len(entry) > 3:
            return entry[3]
        return self.get_value(key)

    def storage(self, value: str) -> dict[str, str | Any] | None:
        raw_value = self.get_value(value, str)
        if not raw_value:
            return None
        options = {}
        if "?" in raw_value:
            value, options = raw_value.split("?", 1)
            options = dict(parse.parse_qsl(options))
        else:
            value = raw_value

        return {"BACKEND": value, "OPTIONS": options}

    def get_default(self, var: str) -> Any:
        var_name = f"{self.prefix}{var}"
        value = ""
        if var_name in self.scheme:
            var_info = self.scheme[var_name]
            value = var_info[1]
            try:
                cast = var_info[0]
                return cast(value)
            except TypeError as e:
                raise TypeError(f"Can't cast {var} to {cast}") from e
        return value


env = SmartEnv(**CONFIG)
