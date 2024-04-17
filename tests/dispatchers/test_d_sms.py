from unittest import mock

import pytest
from strategy_field.utils import fqn
from twilio.base.exceptions import TwilioRestException

from bitcaster.dispatchers.twilio import TwilioSMS
from bitcaster.exceptions import DispatcherError
from bitcaster.models import Channel

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


def test_twilio_error(monkeypatch, smsoutbox):
    ch = Channel(
        dispatcher=fqn(TwilioSMS),
        config={"sid": "__sid__", "token": "__token__", "number": "123456"},
    )
    with mock.patch("twilio.rest.api.Api") as m:
        m.side_effect = TwilioRestException("", "")
        with pytest.raises(DispatcherError):
            assert TwilioSMS(ch).send("123456", "test")


def test_twilio_send(mail_payload, smsoutbox, twilio_sid):
    ch = Channel(
        dispatcher=fqn(TwilioSMS),
        config={"sid": twilio_sid, "token": "__token__", "number": "123456"},
    )

    assert TwilioSMS(ch).send("123456", mail_payload)
