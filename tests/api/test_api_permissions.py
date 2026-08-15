from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from bitcaster.api.permissions import ApiApplicationPermission


class _View(APIView):
    grants: list[str] = []
    kwargs: dict[str, str] = {}


def test_has_permission_rejects_unknown_auth() -> None:
    request = APIRequestFactory().get("/")
    request.auth = "not-a-credential"
    assert ApiApplicationPermission().has_permission(request, _View()) is False


def test_has_object_permission_rejects_unknown_auth() -> None:
    request = APIRequestFactory().get("/")
    request.auth = "not-a-credential"
    assert ApiApplicationPermission().has_object_permission(request, _View(), None) is False


def test_has_permission_rejects_anonymous() -> None:
    request = APIRequestFactory().get("/")
    assert ApiApplicationPermission().has_permission(request, _View()) is False
