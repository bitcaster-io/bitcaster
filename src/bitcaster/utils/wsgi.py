import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """
    Naively yank the first IP address in an X-Forwarded-For header
    and assume this is correct.

    Note: Don't use this in security sensitive situations since this
    value may be forged from a client.
    """
    try:
        return request.META['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    except (KeyError, IndexError):
        return request.META.get('REMOTE_ADDR')
