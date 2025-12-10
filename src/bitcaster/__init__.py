import django_stubs_ext as django_stubs

from .version import __version__

django_stubs.monkeypatch()

VERSION = __version__
