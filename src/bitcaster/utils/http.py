from urllib.parse import urljoin

from constance import config


def absolute_uri(url=None):
    if not url:
        return config.SITE_URL
    return urljoin(config.SITE_URL.rstrip('/') + '/', url.lstrip('/'))
