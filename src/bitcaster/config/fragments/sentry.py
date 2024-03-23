import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from .. import env

SENTRY_DSN = env("SENTRY_DSN")
SENTRY_URL = env("SENTRY_URL")
if SENTRY_DSN:  # pragma: no cover
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=env("SENTRY_ENVIRONMENT"),
        send_default_pii=True,
        enable_tracing=True,
        integrations=[DjangoIntegration(), CeleryIntegration()],
    )
