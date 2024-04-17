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
        # application=Application(from_email=os.environ["TEST_EMAIL_SENDER"], subject_prefix="[mailgun] "),
        # application=Application(from_email=os.environ["TEST_EMAIL_SENDER"], subject_prefix="[mailgun] "),
        dispatcher=fqn(TwilioSMS),
        config={"sid": "__sid__", "token": "__token__", "number": "123456"},
    )
    with mock.patch("twilio.rest.api.Api") as m:
        m.side_effect = TwilioRestException("", "")
        with pytest.raises(DispatcherError):
            assert TwilioSMS(ch).send("123456", "test")


def test_twilio_send(mail_payload, smsoutbox, twilio_sid):
    ch = Channel(
        # application=Application(from_email=os.environ["TEST_EMAIL_SENDER"], subject_prefix="[mailgun] "),
        # application=Application(from_email=os.environ["TEST_EMAIL_SENDER"], subject_prefix="[mailgun] "),
        dispatcher=fqn(TwilioSMS),
        config={"sid": twilio_sid, "token": "__token__", "number": "123456"},
    )

    assert TwilioSMS(ch).send("123456", mail_payload)


#
# def test_twilio(monkeypatch, mail_payload, mocked_responses):
#     from bitcaster.dispatchers import MailgunDispatcher
#     from bitcaster.models import Application, Channel
#
#     def test_send_error(self, assignment): "help")
#
#
#     mocked_responses.add_from_file(file_path=Path(__file__).parent / "mailgun.yaml")
#
#     ch = Channel(
#         application=Application(from_email=os.environ["TEST_EMAIL_SENDER"], subject_prefix="[mailgun] "),
#         config={"api_key": os.environ["MAILGUN_API_KEY"], "sender_domain": os.environ["MAILGUN_SENDER_DOMAIN"]},
#     )
#     MailgunDispatcher(ch).send(os.environ["TEST_EMAIL_RECIPIENT"], mail_payload)
