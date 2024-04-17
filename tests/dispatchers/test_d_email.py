import os
from pathlib import Path
from smtplib import SMTP
from unittest.mock import ANY, Mock, patch

import pytest
from strategy_field.utils import fqn

from bitcaster.dispatchers.base import Payload, dispatcherManager

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


@pytest.fixture()
def mail_payload() -> Payload:
    from bitcaster.models import Application, Event

    return Payload(
        "message",
        event=Event(
            application=Application(
                from_email=os.environ.get("TEST_EMAIL_SENDER"),
                subject_prefix="[Application] ",
            )
        ),
        subject="subject",
        html_message="html_message",
    )


def test_registry():
    from testutils.dispatcher import TestDispatcher

    assert TestDispatcher in dispatcherManager
    assert fqn(TestDispatcher) in dispatcherManager


def test_smtp(mail_payload):
    from bitcaster.dispatchers import EmailDispatcher
    from bitcaster.models import Application, Channel

    with patch("django.core.mail.backends.smtp.smtplib.SMTP", autospec=True) as mock:
        EmailDispatcher(
            Channel(
                application=Application(from_email=os.environ["GMAIL_USER"], subject_prefix="[smtp] "),
                config={
                    "host": "localhost",
                    "port": 25,
                    "username": "test",
                    "password": "<PASSWORD>",
                    "from_email": "sender@example.com",
                },
            )
        ).send("test@example.com", mail_payload)
        mock.assert_called()
        s: Mock[SMTP] = mock.return_value
        s.login.assert_called()
        s.sendmail.assert_called()
        s.sendmail.assert_called_with(from_addr=os.environ["GMAIL_USER"], to_addrs=["test@example.com"], msg=ANY)


def test_gmail(mocked_responses, monkeypatch, mail_payload):
    from bitcaster.dispatchers import GMmailDispatcher
    from bitcaster.models import Application, Channel

    with patch("smtplib.SMTP", autospec=True) as mock:
        ch = Channel(
            application=Application(from_email=os.environ["GMAIL_USER"], subject_prefix="[gmail] "),
            config={
                "username": os.environ["GMAIL_USER"],
                "password": os.environ["GMAIL_PASSWORD"],
            },
        )
        GMmailDispatcher(ch).send("test@example.com", mail_payload)
        mock.assert_called()
        s: Mock[SMTP] = mock.return_value
        s.login.assert_called()
        s.starttls.assert_called()
        s.sendmail.assert_called()
        s.sendmail.assert_called_with(from_addr=os.environ["GMAIL_USER"], to_addrs=["test@example.com"], msg=ANY)


# @_recorder.record(file_path=Path(__file__).parent / "mailjet.yaml")
def test_mailjet(monkeypatch, mail_payload, mocked_responses):
    from bitcaster.dispatchers import MailJetDispatcher
    from bitcaster.models import Application, Channel

    mocked_responses._add_from_file(file_path=Path(__file__).parent / "mailjet.yaml")

    ch = Channel(
        application=Application(from_email=os.environ["TEST_EMAIL_SENDER"], subject_prefix="[mailjet] "),
        config={"api_key": os.environ["MAILJET_API_KEY"], "secret_key": os.environ["MAILJET_SECRET_KEY"]},
    )

    MailJetDispatcher(ch).send(os.environ["TEST_EMAIL_RECIPIENT"], mail_payload)


# @_recorder.record(file_path=Path(__file__).parent / "mailgun.yaml")
def test_mailgun(monkeypatch, mail_payload, mocked_responses):
    from bitcaster.dispatchers import MailgunDispatcher
    from bitcaster.models import Application, Channel

    mocked_responses._add_from_file(file_path=Path(__file__).parent / "mailgun.yaml")

    ch = Channel(
        application=Application(from_email=os.environ["TEST_EMAIL_SENDER"], subject_prefix="[mailgun] "),
        config={"api_key": os.environ["MAILGUN_API_KEY"], "sender_domain": os.environ["MAILGUN_SENDER_DOMAIN"]},
    )
    MailgunDispatcher(ch).send(os.environ["TEST_EMAIL_RECIPIENT"], mail_payload)


#
# def test_twilio(monkeypatch, mail_payload, mocked_responses):
#     from bitcaster.dispatchers import MailgunDispatcher
#     from bitcaster.models import Application, Channel
#
#     mocked_responses.add_from_file(file_path=Path(__file__).parent / "mailgun.yaml")
#
#     ch = Channel(
#         application=Application(from_email=os.environ["TEST_EMAIL_SENDER"], subject_prefix="[mailgun] "),
#         config={"api_key": os.environ["MAILGUN_API_KEY"], "sender_domain": os.environ["MAILGUN_SENDER_DOMAIN"]},
#     )
#     MailgunDispatcher(ch).send(os.environ["TEST_EMAIL_RECIPIENT"], mail_payload)
