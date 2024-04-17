from typing import TYPE_CHECKING
from urllib.parse import parse_qsl

import pytest

if TYPE_CHECKING:
    from bitcaster.dispatchers.base import Payload

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


@pytest.fixture()
def mail_payload(request) -> "Payload":
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
def twilio_sid():
    return "__sid__"


@pytest.fixture()
def smsoutbox(mocked_responses, twilio_sid):
    sms_list = []

    def create_address_callback(request):
        payload = dict(parse_qsl(request.body))
        sms_list.append(payload)
        return 200, {}, "{}"

    mocked_responses.add_callback(
        mocked_responses.POST,
        f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json",
        callback=create_address_callback,
    )

    return sms_list
