import os
from smtplib import SMTP
from unittest.mock import ANY, Mock, patch

import pytest
from django.core.exceptions import ValidationError

from bitcaster.dispatchers import GMmailDispatcher

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


@pytest.mark.parametrize("mail_payload", ("", "html_message"), indirect=True)
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


def test_config():
    d = GMmailDispatcher(Mock(config={}))
    with pytest.raises(ValidationError):
        d.config
