from typing import TYPE_CHECKING, TypedDict
from unittest import mock
from unittest.mock import MagicMock

import pytest
from rest_framework.test import APIClient
from testutils.factories.event import EventFactory
from testutils.factories.key import ApiKeyFactory
from testutils.perms import key_grants

from bitcaster.api.permissions import ApiApplicationPermission, ApiBasePermission
from bitcaster.api.urls import EventTrigger
from bitcaster.auth.constants import Grant

if TYPE_CHECKING:
    from bitcaster.models import ApiKey, Event

    Context = TypedDict(
        "Context",
        {"event": Event, "key": ApiKey, "backend": ApiApplicationPermission, "view": EventTrigger},
    )

pytestmark = [pytest.mark.api, pytest.mark.django_db]


@pytest.fixture()
def client() -> APIClient:
    c = APIClient()
    return c


@pytest.fixture()
def context(admin_user) -> "Context":
    event: "Event" = EventFactory()
    key = ApiKeyFactory(user=admin_user, grants=[], application=event.application)
    return {
        "event": event,
        "key": key,
        "backend": ApiApplicationPermission(),
        "view": MagicMock(specs=EventTrigger.as_view()),
    }


@pytest.mark.parametrize("g", [g for g in Grant])
def test_has_specific_permission(rf, g, context: "Context") -> None:
    api_key: ApiKey = context["key"]
    p: ApiBasePermission = context["backend"]
    view: "EventTrigger" = context["view"]
    req = rf.get("/")

    with mock.patch.object(req, "auth", api_key, create=True):
        with mock.patch.object(view, "grants", [g], create=True):
            with key_grants(api_key, [g]):
                assert p.has_permission(req, view)


def test_scope(rf, context: "Context") -> None:
    api_key: ApiKey = context["key"]
    p: ApiBasePermission = context["backend"]
    view: "EventTrigger" = context["view"]
    event: "Event" = context["event"]

    req = rf.get("/")

    view.required_grants = [Grant.SYSTEM_PING]

    with mock.patch.object(req, "auth", api_key, create=True):
        with key_grants(api_key, [Grant.SYSTEM_PING], application=None):
            with mock.patch.object(view, "grants", [Grant.SYSTEM_PING]):
                assert p.has_permission(req, view)
                assert p.has_object_permission(req, view, event)


def test_has_permission(rf, context: "Context") -> None:
    api_key: ApiKey = context["key"]
    p: ApiBasePermission = context["backend"]
    view: "EventTrigger" = context["view"]
    req = rf.get("/")

    assert not p.has_permission(req, MagicMock())

    with mock.patch.object(req, "auth", None, create=True):
        assert not p.has_permission(req, MagicMock())

    with mock.patch.object(req, "auth", api_key, create=True):
        with mock.patch.object(view, "grants", [Grant.SYSTEM_PING], create=True):
            with mock.patch.object(view, "required_grants", [Grant.SYSTEM_PING], create=True):
                with key_grants(api_key, None):
                    assert not p.has_permission(req, view)

                with key_grants(api_key, None):
                    assert not p.has_permission(req, view)

        with mock.patch.object(view, "grants", [Grant.SYSTEM_PING], create=True):
            with mock.patch.object(view, "required_grants", [Grant.SYSTEM_PING], create=True):
                with key_grants(api_key, Grant.SYSTEM_PING):
                    assert p.has_permission(req, view)


def test_user_inactive(rf, context: "Context") -> None:
    from django.contrib.auth.models import AnonymousUser

    api_key: ApiKey = context["key"]
    p: ApiBasePermission = context["backend"]
    view: "EventTrigger" = context["view"]
    req = rf.get("/")

    with mock.patch.object(req, "user", AnonymousUser(), create=True):
        with mock.patch.object(req, "auth", api_key, create=True):
            with mock.patch.object(view, "grants", [Grant.SYSTEM_PING]):
                with mock.patch.object(view, "required_grants", [Grant.SYSTEM_PING]):
                    with key_grants(api_key, None):
                        assert not p.has_permission(req, view)


def test_has_object_permission(rf, context: "Context") -> None:
    api_key: ApiKey = context["key"]
    p: ApiBasePermission = context["backend"]
    view: "EventTrigger" = context["view"]
    event: "Event" = context["event"]
    req = rf.get("/")
    assert not p.has_permission(req, MagicMock())

    with mock.patch.object(req, "auth", None, create=True):
        assert not p.has_object_permission(req, MagicMock(), event)

    with mock.patch.object(req, "auth", api_key, create=True):
        with mock.patch.object(view, "grants", [Grant.SYSTEM_PING]):
            with mock.patch.object(view, "required_grants", [Grant.SYSTEM_PING]):
                with key_grants(api_key, None):
                    assert not p.has_object_permission(req, view, event)

        with key_grants(api_key, None):
            assert not p.has_object_permission(req, view, event)

        with mock.patch.object(view, "grants", [Grant.SYSTEM_PING]):
            with key_grants(api_key, Grant.SYSTEM_PING):
                assert p.has_object_permission(req, view, event)
