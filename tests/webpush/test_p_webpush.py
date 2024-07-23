from unittest.mock import Mock

import pytest
from django.core.exceptions import ValidationError
from pytest import FixtureRequest, MonkeyPatch
from responses import RequestsMock

from bitcaster.dispatchers.base import Payload
from bitcaster.exceptions import DispatcherError
from bitcaster.models import Assignment
from bitcaster.state import state
from bitcaster.webpush.dispatcher import WebPushConfig, WebPushDispatcher

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


@pytest.fixture()
def payload(request: FixtureRequest) -> "Payload":
    from testutils.factories import ApplicationFactory

    from bitcaster.models import Event

    return Payload(
        "message",
        event=Event(application=ApplicationFactory()),
        subject="subject",
        html_message=getattr(request, "param", ""),
    )


def test_webpush(
    monkeypatch: MonkeyPatch,
    payload: Payload,
    mocked_responses: RequestsMock,
    push_assignment: "Assignment",
    fcm_url: str,
) -> None:
    mocked_responses.add(mocked_responses.POST, fcm_url)
    WebPushDispatcher(push_assignment.channel).send(push_assignment.address.value, payload, push_assignment)


def test_webpush_error(
    monkeypatch: MonkeyPatch,
    payload: Payload,
    mocked_responses: RequestsMock,
    push_assignment: "Assignment",
    fcm_url: str,
) -> None:
    with pytest.raises(DispatcherError) as e:
        WebPushDispatcher(push_assignment.channel).send(push_assignment.address.value, payload)
    assert str(e.value) == "WebPushDispatcher: assignment arg must be provided"


def test_webpush_not_subscribed(
    monkeypatch: MonkeyPatch, payload: Payload, mocked_responses: RequestsMock, assignment: "Assignment", fcm_url: str
) -> None:
    with pytest.raises(DispatcherError) as e:
        WebPushDispatcher(assignment.channel).send(assignment.address.value, payload, assignment)
    assert str(e.value) == "Assignment not subscribed"


def test_config() -> None:
    with state.configure(request=Mock()):
        d: WebPushDispatcher = WebPushDispatcher(Mock(config={}))
        with pytest.raises(ValidationError):
            d.config


def test_form() -> None:
    with state.configure(request=Mock()):
        frm = WebPushConfig(data={})
        assert not frm.is_valid()

        frm = WebPushConfig(
            data={
                "private_key": "nFUEzMGtnCgQkAsYJ9iQOjWHquTTfrOwyzvZeUiChgc",
                "application_id": "12345678",
                "email": "test@example.com",
            }
        )
        assert frm.is_valid(), frm.errors


def test_form2() -> None:
    with state.configure(request=Mock()):
        frm = WebPushConfig(data={}, initial={"email": "test@example.com"})
        assert not frm.is_valid()

        frm = WebPushConfig(
            data={
                "private_key": "nFUEzMGtnCgQkAsYJ9iQOjWHquTTfrOwyzvZeUiChgc",
                "application_id": "12345678",
                "email": "test@example.com",
            }
        )
        assert frm.is_valid(), frm.errors
