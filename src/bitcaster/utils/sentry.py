import logging
from urllib.parse import ParseResult, urlparse

from django.conf import settings

logger = logging.getLogger(__name__)


def get_sentry_host() -> str:
    result: ParseResult = urlparse(settings.SENTRY_DSN)
    host = f"{result.scheme}://{result.hostname}"
    if result.port:
        host = f"{host}:{result.port}"

    return host


def get_sentry_dashboard() -> str:
    return f"{get_sentry_host()}/{settings.SENTRY_PROJECT}"


def get_event_url(event_id: str) -> str:
    try:
        return f"{get_sentry_host()}/{settings.SENTRY_PROJECT}/?query={event_id}"
    except Exception as e:
        logger.exception(e)
