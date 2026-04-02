import sentry_sdk
from django.conf import settings
from sentry_sdk.integrations.django import DjangoIntegration


def init_sentry(raise_exception: bool = False) -> bool:
    try:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT,
            send_default_pii=True,
            enable_tracing=True,
            integrations=[
                DjangoIntegration(),
            ],
        )
        return True
    except Exception:
        if raise_exception:
            raise
        return False
