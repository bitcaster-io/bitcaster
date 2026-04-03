from ...utils.sentry import init_sentry
from ..settings import env

SENTRY_DSN = env("SENTRY_DSN")
SENTRY_URL = env("SENTRY_URL")
SENTRY_ENVIRONMENT = env("SENTRY_ENVIRONMENT")

if SENTRY_DSN:  # pragma: no cover
    init_sentry()
