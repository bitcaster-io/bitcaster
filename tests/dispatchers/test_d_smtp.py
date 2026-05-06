import os

import pytest
from unittest.mock import ANY, Mock, patch

from bitcaster.dispatchers.base import Payload
from bitcaster.exceptions import DispatcherError

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


@pytest.fixture
def html_payload(mail_payload: Payload) -> Payload:
    mail_payload.html_message = "<h1></h1>"
    return mail_payload


@pytest.mark.parametrize("payload", [pytest.param("mail_payload"), pytest.param("html_payload")])
def test_smtp(request, payload: Payload) -> None:
    from bitcaster.dispatchers import EmailDispatcher
    from bitcaster.models import Channel, Project

    mail_payload = request.getfixturevalue(payload)

    with patch("django.core.mail.backends.smtp.smtplib.SMTP", autospec=True) as mock:
        EmailDispatcher(
            Channel(
                project=Project(from_email=os.environ["GMAIL_USER"], subject_prefix="[gmail] "),
                config={
                    "host": "localhost",
                    "port": 25,
                    "username": "test",
                    "password": "<PASSWORD>",
                    "from_email": "sender@example.com",
                    "timeout": 3,
                },
            )
        ).send("test@example.com", mail_payload)
        mock.assert_called()
        s: Mock = mock.return_value
        s.login.assert_called()
        s.sendmail.assert_called()
        s.sendmail.assert_called_with(from_addr=os.environ["GMAIL_USER"], to_addrs=["test@example.com"], msg=ANY)


@pytest.mark.parametrize("error", ["is an invalid email address", "server unreachable"])
def test_smtp_invalid_recipient(mail_payload: Payload, error: str) -> None:
    from bitcaster.dispatchers import EmailDispatcher
    from bitcaster.models import Channel, Project

    with patch("django.core.mail.EmailMultiAlternatives.send", side_effect=Exception(error)):
        d = EmailDispatcher(
            Channel(
                project=Project(from_email=os.environ["GMAIL_USER"], subject_prefix="[gmail] "),
                config={
                    "host": "localhost",
                    "port": 25,
                    "username": "test",
                    "password": "<PASSWORD>",
                    "from_email": "--",
                    "timeout": 3,
                },
            )
        )
        with pytest.raises(DispatcherError):
            d.send("===", mail_payload)
