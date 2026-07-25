import requests

import pytest
from testutils.docker import ContainerHost

pytestmark = pytest.mark.docker

CLIENT = (
    'python3 -c "'
    "import http.client; "
    "c = http.client.HTTPConnection('localhost', 8000); "
    "c.request('GET', '{url}'); "
    "r = c.getresponse(); "
    "print(r.status); print(r.read().decode())"
    '"'
)


def test_healthcheck_returns_200(started_server) -> None:
    result = started_server.run(CLIENT.format(url="/healthcheck/"))
    assert result.rc == 0
    lines = result.stdout.strip().splitlines()

    assert lines[0] == "200"
    assert "Ok" in lines[1]


def test_url_admin(started_server) -> None:
    result = started_server.run(CLIENT.format(url="/admin/"))
    assert result.rc == 0
    lines = result.stdout.strip().splitlines()
    assert lines[0] in ("301", "302", "200")


def test_homepage_returns_response(started_server: ContainerHost) -> None:
    started_server.lastlog()
    res = requests.get("http://localhost:8003")
    assert "Login" in res.text
    assert res.status_code == 200
    requests.get("http://localhost:8003/admin/")
    assert "GET /admin/" in started_server.lastlog()
