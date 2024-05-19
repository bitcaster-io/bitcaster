import os
from smtplib import SMTP
from unittest.mock import ANY, Mock, patch

import pytest

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


def test_smtp(mail_payload):
    from bitcaster.dispatchers import EmailDispatcher
    from bitcaster.models import Channel, Project

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
                },
            )
        ).send("test@example.com", mail_payload)
        mock.assert_called()
        s: Mock[SMTP] = mock.return_value
        s.login.assert_called()
        s.sendmail.assert_called()
        s.sendmail.assert_called_with(from_addr=os.environ["GMAIL_USER"], to_addrs=["test@example.com"], msg=ANY)
