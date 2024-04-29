from typing import TYPE_CHECKING, TypedDict
from unittest.mock import MagicMock

import pytest
from rest_framework.test import APIClient
from testutils.factories.event import EventFactory
from testutils.factories.key import ApiKeyFactory
from testutils.perms import key_grants

from bitcaster.api.permissions import ApiApplicationPermission
from bitcaster.api.views import EventViewSet
from bitcaster.auth.constants import Grant

if TYPE_CHECKING:
    from bitcaster.models import ApiKey, Event, User

    Context = TypedDict(
        "Context",
        {
            "event": Event,
            "key": ApiKey,
            "user": User,
        },
    )

pytestmark = [pytest.mark.api, pytest.mark.django_db]

# WE DO NOT USE REVERSE HERE. WE NEED TO CHECK ENDPOINTS CONTRACTS


@pytest.fixture()
def client() -> APIClient:
    c = APIClient()
    return c


@pytest.fixture()
def data(admin_user) -> "Context":
    event: "Event" = EventFactory()
    key = ApiKeyFactory(user=admin_user, grants=[], application=event.application)
    return {
        "event": event,
        "key": key,
        "user": admin_user,
    }


def test_has_permission(rf, api_key) -> None:
    p = ApiApplicationPermission()
    req = rf.get("/api/permissions/")
    req.auth = None
    view: "EventViewSet" = MagicMock(spec=EventViewSet)

    assert not p.has_permission(req, MagicMock())
    req.auth = api_key

    with key_grants(api_key, None):
        assert not p.has_permission(req, view)

    view.required_grants = [Grant.SYSTEM_PING]
    with key_grants(api_key, None):
        assert not p.has_permission(req, view)

    view.required_grants = [Grant.SYSTEM_PING]
    view.grants = [Grant.SYSTEM_PING]
    with key_grants(api_key, Grant.SYSTEM_PING):
        assert p.has_permission(req, view)


def test_has_object_permission(rf, api_key, event, application) -> None:
    p = ApiApplicationPermission()
    req = rf.get("/api/permissions/")
    req.auth = None
    view: "EventViewSet" = MagicMock(spec=EventViewSet)

    assert not p.has_object_permission(req, view, event)
    req.auth = api_key

    with key_grants(api_key, None):
        assert not p.has_object_permission(req, view, event)

    view.required_grants = [Grant.SYSTEM_PING]
    with key_grants(api_key, None):
        assert not p.has_object_permission(req, view, event)

    view.required_grants = [Grant.SYSTEM_PING]
    view.grants = [Grant.SYSTEM_PING]

    with key_grants(api_key, Grant.SYSTEM_PING):
        assert not p.has_object_permission(req, view, event)

    with key_grants(api_key, Grant.SYSTEM_PING, application=application):
        assert not p.has_object_permission(req, view, event)

    with key_grants(api_key, Grant.SYSTEM_PING, application=event.application):
        assert p.has_object_permission(req, view, event)
