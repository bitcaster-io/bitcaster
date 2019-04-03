from urllib.parse import urlencode, urljoin

from constance import config


def absolute_uri(url=None):
    if not url:
        return config.SITE_URL
    return urljoin(config.SITE_URL.rstrip('/') + '/', url.lstrip('/'))


def get_query_string(request, new_params=None, remove=None):
    params = dict(request.GET.items())
    if new_params is None:
        new_params = {}
    if remove is None:
        remove = []
    p = params.copy()
    for r in remove:
        for k in list(p):
            if k.startswith(r):
                del p[k]
    for k, v in new_params.items():
        if v is None:
            if k in p:
                del p[k]
        else:
            p[k] = v
    return '?%s' % urlencode(sorted(p.items()))
