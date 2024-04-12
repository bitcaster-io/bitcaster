import os
from pathlib import Path

import pytest
from django.core.mail import EmailMultiAlternatives
from strategy_field.utils import fqn
from testutils.decorators import requires_env

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
    )


def test_registry():
    from testutils.dispatcher import TestDispatcher

    assert TestDispatcher in dispatcherManager
    assert fqn(TestDispatcher) in dispatcherManager


@requires_env("GMAIL_USER", "GMAIL_PASSWORD", "TEST_EMAIL_RECIPIENT")
def test_smtp(mocked_responses, monkeypatch, mailoutbox, mail_payload):
    from bitcaster.dispatchers import EmailDispatcher
    from bitcaster.models import Application, Channel

    EmailDispatcher.backend = "django.core.mail.backends.locmem.EmailBackend"
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
    msg: EmailMultiAlternatives = mailoutbox[0]
    assert msg.to == ["test@example.com"]
    assert msg.subject == "[smtp] subject"
    assert msg.body == "message"


@requires_env("GMAIL_USER", "GMAIL_PASSWORD", "TEST_EMAIL_RECIPIENT")
def test_gmail(mocked_responses, monkeypatch, mailoutbox, mail_payload):
    from bitcaster.dispatchers import GMmailDispatcher
    from bitcaster.models import Application, Channel

    # GMmailDispatcher.backend = "django.core.mail.backends.locmem.EmailBackend"
    ch = Channel(
        application=Application(from_email=os.environ["GMAIL_USER"], subject_prefix="[gmail] "),
        config={
            "username": os.environ["GMAIL_USER"],
            "password": os.environ["GMAIL_PASSWORD"],
        },
    )
    GMmailDispatcher(ch).send(os.environ["GMAIL_USER"], mail_payload)


# @requires_env("MAILJET_API_KEY", "MAILJET_SECRET_KEY", "TEST_EMAIL_RECIPIENT")
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


# @requires_env("MAILGUN_API_KEY", "MAILGUN_SENDER_EMAIL", "MAILGUN_RECIPIENT_EMAIL")
# @_recorder.record(file_path=Path(__file__).parent / "mailgun.yaml")
def test_mailgun(monkeypatch, mail_payload, mocked_responses):
    from bitcaster.dispatchers import MailgunDispatcher
    from bitcaster.models import Application, Channel

    mocked_responses._add_from_file(file_path=Path(__file__).parent / "mailgun.yaml")

    # mocked_responses.add("POST", "https://api.mailjet.com/v3.1/send", json={"Messages": [{"Status": "success"}]})

    ch = Channel(
        application=Application(from_email=os.environ["TEST_EMAIL_SENDER"], subject_prefix="[mailgun] "),
        config={"api_key": os.environ["MAILGUN_API_KEY"], "sender_domain": os.environ["MAILGUN_SENDER_DOMAIN"]},
    )
    MailgunDispatcher(ch).send(os.environ["TEST_EMAIL_RECIPIENT"], mail_payload)
