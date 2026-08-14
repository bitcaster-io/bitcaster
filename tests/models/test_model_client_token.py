from typing import TYPE_CHECKING

import pytest

from django.core.exceptions import ValidationError
from django.utils import timezone

from bitcaster.models import ClientToken

if TYPE_CHECKING:
    from bitcaster.models import ApiKey, Application, User

pytestmark = [pytest.mark.django_db]


def _make(
    application: "Application",
    user: "User",
    parent: "ApiKey | None" = None,
    event=None,
    allowed_origins: "list[str] | None" = None,
    **kwargs,
) -> ClientToken:
    if allowed_origins is None:
        allowed_origins = ["https://example.com"]
    return ClientToken(
        user=user,
        parent=parent,
        organization=application.project.organization,
        project=application.project,
        application=application,
        event=event,
        allowed_origins=allowed_origins,
        expires_at=timezone.now() + kwargs.pop("ttl", None) if "ttl" in kwargs else timezone.now(),
        **kwargs,
    )


def test_client_token_clean_ok(application: "Application", user: "User") -> None:
    token = _make(application, user)
    token.clean()  # must not raise


def test_client_token_clean_requires_application(user: "User") -> None:
    from testutils.factories import OrganizationFactory

    token = ClientToken(
        user=user,
        organization=OrganizationFactory(),
        allowed_origins=["https://example.com"],
        expires_at=timezone.now(),
    )
    with pytest.raises(ValidationError):
        token.clean()


def test_client_token_clean_requires_origins(application: "Application", user: "User") -> None:
    token = _make(application, user, allowed_origins=[])
    with pytest.raises(ValidationError):
        token.clean()


def test_client_token_clean_event_must_belong_to_application(application: "Application", user: "User") -> None:
    from testutils.factories import EventFactory

    other_event = EventFactory()
    token = _make(application, user, event=other_event)
    with pytest.raises(ValidationError):
        token.clean()


def test_client_token_clean_event_ok(application: "Application", user: "User") -> None:
    from testutils.factories import EventFactory

    event = EventFactory(application=application)
    token = _make(application, user, event=event)
    token.clean()  # must not raise


def test_client_token_clean_requires_expires_at(application: "Application", user: "User") -> None:
    token = _make(application, user)
    token.expires_at = None
    with pytest.raises(ValidationError):
        token.clean()


def test_client_token_is_web(application: "Application", user: "User") -> None:
    token = _make(application, user)
    assert token.is_web() is True
    assert token.grants == ["WEB_TRIGGER"]


def test_client_token_save_runs_full_clean(application: "Application", user: "User") -> None:
    token = ClientToken(
        user=user,
        organization=application.project.organization,
        project=application.project,
        allowed_origins=["https://example.com"],
        expires_at=timezone.now(),
    )
    with pytest.raises(ValidationError):
        token.save()


def test_client_token_expires_at_required_by_model(application: "Application", user: "User") -> None:
    token = _make(application, user)
    assert token._meta.get_field("expires_at").null is False
