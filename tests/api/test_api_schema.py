from typing import TYPE_CHECKING

import pytest
from rest_framework.test import APIClient

if TYPE_CHECKING:
    from bitcaster.models import User

pytestmark = [pytest.mark.api, pytest.mark.django_db]

# WE DO NOT USE REVERSE HERE. WE NEED TO CHECK ENDPOINTS CONTRACTS


@pytest.fixture()
def client(admin_user: "User") -> APIClient:
    c = APIClient()
    c.force_authenticate(user=admin_user)
    return c


#
# def test_api_root(client):
#     url = "/api/"
#     res = client.get(url)
#     assert res.json()


def test_api_schema(client: APIClient) -> None:
    url = "/api/raw/"
    res = client.get(url)
    assert res.status_code == 200
    assert res["Content-Type"] == "application/vnd.oai.openapi; charset=utf-8"


def test_api_swagger(client: APIClient) -> None:
    url = "/api/"
    res = client.get(url)
    assert res.status_code == 200
    assert res["Content-Type"] == "text/html; charset=utf-8"


def test_api_redoc(client: APIClient) -> None:
    url = "/api/redoc/"
    res = client.get(url)
    assert res.status_code == 200
    assert res["Content-Type"] == "text/html; charset=utf-8"
