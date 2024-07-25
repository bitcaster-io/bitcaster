from typing import TYPE_CHECKING

import pytest
from django.urls import reverse
from django_webtest import DjangoTestApp

from bitcaster.webpush.utils import sign

if TYPE_CHECKING:
    from pytest import MonkeyPatch

    from bitcaster.models import Application, Assignment


@pytest.fixture
def push_assignment() -> "Assignment":
    from testutils.factories import AssignmentFactory, ChannelFactory

    ch = ChannelFactory(config={"APPLICATION_SERVER_KEY": "aa", "private_key": "aaa"})
    return AssignmentFactory(channel=ch)


def test_push_serviceworker(django_app: DjangoTestApp, application: "Application") -> None:
    url = reverse("webpush:service_worker", args=[application.slug])
    res = django_app.get(url)
    assert res.status_code == 200


def test_push_ask(django_app: DjangoTestApp, push_assignment: "Assignment", monkeypatch: "MonkeyPatch") -> None:
    secret = sign(push_assignment)
    url = reverse("webpush:ask", args=[secret])
    res = django_app.get(url)
    assert res.status_code == 200


def test_push_subscribe(django_app: DjangoTestApp, push_assignment: "Assignment", monkeypatch: "MonkeyPatch") -> None:
    secret = sign(push_assignment)
    url = reverse("webpush:subscribe", args=[secret])
    res = django_app.post_json(
        url,
        {
            "endpoint": "fcm_url",
            "keys": {
                "auth": "mp1NVQZ7lk8l991jv_IaZg",
                "p256dh": "BF2k3PvW7s7wHlR9jvTD5vOvE4y8xaWHp73lpIE6u9dUXD0Y1J6fKEMW69rlvmAx--7hNMbWQ149w2g3xP8QCg",
            },
        },
    )
    assert res.status_code == 201


def test_push_subscribe_404(
    django_app: DjangoTestApp, push_assignment: "Assignment", monkeypatch: "MonkeyPatch"
) -> None:
    secret = sign(push_assignment)
    push_assignment.delete()
    url = reverse("webpush:subscribe", args=[secret])
    res = django_app.post_json(url, {}, expect_errors=True)
    assert res.status_code == 404


def test_push_unsubscribe(django_app: DjangoTestApp, push_assignment: "Assignment", monkeypatch: "MonkeyPatch") -> None:
    secret = sign(push_assignment)
    url = reverse("webpush:unsubscribe", args=[secret])
    res = django_app.post_json(url)
    assert res.status_code == 200


def test_push_data(django_app: DjangoTestApp, push_assignment: "Assignment", monkeypatch: "MonkeyPatch") -> None:
    secret = sign(push_assignment)
    url = reverse("webpush:data", args=[secret])
    res = django_app.get(url)
    assert res.status_code == 200
