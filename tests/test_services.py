# -*- coding: utf-8 -*-
from unittest.mock import Mock

from bitcaster.services.http import DevHTTPServer


def test_http(monkeypatch):
    monkeypatch.setattr('gunicorn.arbiter.Arbiter.init_signals', Mock())

    http = DevHTTPServer(port=19000, workers=1, pidfile='aaa.pid', daemonize=False)
    assert http.host == 'localhost'
    assert http.port == 19000
    assert http.app.options['bind'] == 'localhost:19000'
