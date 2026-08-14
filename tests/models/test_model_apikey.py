import pytest

from django.core.exceptions import ValidationError

from bitcaster.auth.constants import Grant
from bitcaster.models import ApiKey, Application, User
from bitcaster.models.key import KeyKind


def test_manager_get_or_create(application: "Application", user: "User") -> None:
    assert ApiKey.objects.get_or_create(user=user, application=application)
    assert ApiKey.objects.get_or_create(user=user, project=application.project)
    assert ApiKey.objects.get_or_create(user=user, organization=application.project.organization)

    assert ApiKey.objects.get_or_create(user=user, defaults={"application": application})
    assert ApiKey.objects.get_or_create(user=user, defaults={"project": application.project})
    assert ApiKey.objects.get_or_create(user=user, defaults={"organization": application.project.organization})


def test_manager_update_or_create(application: "Application", user: "User") -> None:
    assert ApiKey.objects.update_or_create(user=user, application=application)
    assert ApiKey.objects.update_or_create(user=user, project=application.project)
    assert ApiKey.objects.update_or_create(user=user, organization=application.project.organization)

    assert ApiKey.objects.update_or_create(user=user, defaults={"application": application})
    assert ApiKey.objects.update_or_create(user=user, defaults={"project": application.project})
    assert ApiKey.objects.update_or_create(user=user, defaults={"organization": application.project.organization})


def test_public_key_valid(application: "Application", user: "User") -> None:
    key = ApiKey(name="k", user=user, application=application, kind=KeyKind.PUBLIC, origins=["https://example.com"])
    key.full_clean()


def test_public_key_requires_application(application: "Application", user: "User") -> None:
    key = ApiKey(name="k", user=user, kind=KeyKind.PUBLIC, origins=["https://example.com"])
    with pytest.raises(ValidationError):
        key.full_clean()


def test_public_key_requires_trigger_grant(application: "Application", user: "User") -> None:
    key = ApiKey(
        name="k",
        user=user,
        application=application,
        kind=KeyKind.PUBLIC,
        origins=["https://example.com"],
        grants=[Grant.EVENT_TRIGGER, Grant.EVENT_LIST],
    )
    with pytest.raises(ValidationError):
        key.full_clean()


def test_public_key_requires_origin(application: "Application", user: "User") -> None:
    key = ApiKey(name="k", user=user, application=application, kind=KeyKind.PUBLIC)
    with pytest.raises(ValidationError):
        key.full_clean()


def test_public_key_invalid_origin(application: "Application", user: "User") -> None:
    key = ApiKey(name="k", user=user, application=application, kind=KeyKind.PUBLIC, origins=["not-an-origin"])
    with pytest.raises(ValidationError):
        key.full_clean()


def test_server_key_origin_not_required(application: "Application", user: "User") -> None:
    key = ApiKey(name="k", user=user, application=application, kind=KeyKind.SERVER, grants=[Grant.EVENT_TRIGGER])
    key.full_clean()


def test_public_key_allowed_events_valid(application: "Application", user: "User") -> None:
    from testutils.factories import EventFactory

    event = EventFactory(application=application)
    key = ApiKey(
        name="k",
        user=user,
        application=application,
        kind=KeyKind.PUBLIC,
        origins=["https://example.com"],
        allowed_events=[event.slug],
    )
    key.full_clean()


def test_public_key_allowed_events_unknown(application: "Application", user: "User") -> None:
    key = ApiKey(
        name="k",
        user=user,
        application=application,
        kind=KeyKind.PUBLIC,
        origins=["https://example.com"],
        allowed_events=["unknown-event"],
    )
    with pytest.raises(ValidationError):
        key.full_clean()


def test_allowed_events_requires_application(user: "User") -> None:
    key = ApiKey(name="k", user=user, allowed_events=["some-event"])
    with pytest.raises(ValidationError):
        key.full_clean()
