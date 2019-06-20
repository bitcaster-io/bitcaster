from _md5 import md5
from urllib.parse import urlencode

from jinja2 import environment
from slugify import slugify

environment.DEFAULT_FILTERS['md5'] = lambda s: md5(s.encode('utf-8'))
environment.DEFAULT_FILTERS['hexdigest'] = lambda s: s.hexdigest()
environment.DEFAULT_FILTERS['urlencode'] = urlencode
environment.DEFAULT_FILTERS['slugify'] = slugify
