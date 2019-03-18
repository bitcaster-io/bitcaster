from urllib.parse import urljoin

from constance import config
from constance.test import override_config


@override_config(SITE_URL='http://demo/')
def absolute_uri(url=None):
    if not url:
        return config.SITE_URL
    return urljoin(config.SITE_URL.rstrip('/') + '/', url.lstrip('/'))
