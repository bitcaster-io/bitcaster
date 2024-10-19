from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qsl

import pytest
from requests import PreparedRequest
from responses import RequestsMock

if TYPE_CHECKING:
    from pytest import FixtureRequest

    from bitcaster.dispatchers.base import Payload
pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


@pytest.fixture()
def mail_payload(request: "FixtureRequest") -> "Payload":
    from testutils.factories import ApplicationFactory

    from bitcaster.dispatchers.base import Payload
    from bitcaster.models import Event

    return Payload(
        "message",
        event=Event(application=ApplicationFactory()),
        subject="subject",
        html_message=getattr(request, "param", ""),
    )


@pytest.fixture()
def twilio_sid() -> str:
    return "__sid__"


@pytest.fixture()
def smsoutbox(mocked_responses: "RequestsMock", twilio_sid: str) -> list[Any]:
    sms_list = []

    def create_address_callback(request: "PreparedRequest") -> tuple[int, dict[str, str], str]:
        payload = dict(parse_qsl(str(request.body)))
        sms_list.append(payload)
        return 200, {}, "{}"

    mocked_responses.add_callback(
        mocked_responses.POST,
        f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json",
        callback=create_address_callback,
    )

    return sms_list
