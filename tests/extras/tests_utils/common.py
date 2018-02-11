import os
import socket
from contextlib import contextmanager
from django.contrib.sessions.backends.base import SessionBase
from django.http import HttpRequest

import pytest


class override_threadlocals(object):
    """
    context manager to set current request attributes
    ::

    with override_threadlocals(user=User.object.get(pk=1)
        ...
        ...

    """

    def __init__(self, **kwargs):
        # self.wrapped_request = middleware.get_current_request
        # self.backup = getattr(middleware._thread_locals, 'request', None)

        self.request = kwargs.pop('request', None)
        self.args = kwargs

    def __enter__(self):
        self.enable()

    def __exit__(self, exc_type, exc_value, traceback):
        self.disable()

    def enable(self):
        # middleware.get_current_request.cache_clear()
        # def _inner_request():
        req = self.request or HttpRequest()
        for attr_name, value in self.args.items():
            setattr(req, attr_name, value)
        # return req

        # setattr(middleware._thread_locals, 'request', req)
        # middleware.get_current_request = _inner_request

    def disable(self):
        pass
    #     setattr(middleware._thread_locals, 'request', self.backup)


class SessionStore(SessionBase):
    def __init__(self, session_key=None, **kwargs):
        super().__init__(session_key)
        self._session_cache = kwargs

    def delete(self, session_key=None):
        pass


class current_request(override_threadlocals):
    def __init__(self, request, **kwargs):
        super(current_request, self).__init__(request=request, **kwargs)


class current_user(override_threadlocals):
    """
    context manager to set the user for running thread
    """

    def __init__(self, user, **kwargs):
        kwargs = {'user': user}
        super(current_user, self).__init__(**kwargs)


@contextmanager
def temp_environ(**kwargs):
    _environ = dict(os.environ)
    for k, v in kwargs.items():
        os.environ[k] = v
    yield
    os.environ.clear()
    os.environ.update(_environ)


def is_connected():
    try:
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False


skip_if_no_network = pytest.mark.skipif(not is_connected(),
                                        reason="no network")
xfail_if_no_network = pytest.mark.xfail(not is_connected(),
                                        reason="no network")
