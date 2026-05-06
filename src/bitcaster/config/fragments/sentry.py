from bitcaster.config.settings import env
from bitcaster.utils.sentry import init_sentry

SENTRY_DSN = env("SENTRY_DSN")
SENTRY_URL = env("SENTRY_URL")
SENTRY_ENVIRONMENT = env("SENTRY_ENVIRONMENT")

if SENTRY_DSN:  # pragma: no cover
    init_sentry()
