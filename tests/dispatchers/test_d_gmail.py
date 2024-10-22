import os
from typing import TYPE_CHECKING
from unittest.mock import ANY, Mock, patch

import pytest
from django.core.exceptions import ValidationError
from responses import RequestsMock

from bitcaster.dispatchers import GMailDispatcher

if TYPE_CHECKING:
    from bitcaster.dispatchers.base import Payload

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


@pytest.mark.parametrize("mail_payload", ("", "html_message"), indirect=True)
def test_gmail_send(mocked_responses: "RequestsMock", mail_payload: "Payload") -> None:
    from bitcaster.dispatchers import GMailDispatcher
    from bitcaster.models import Channel, Project

    with patch("smtplib.SMTP", autospec=True) as mock:
        ch = Channel(
            project=Project(from_email=os.environ["GMAIL_USER"], subject_prefix="[gmail] "),
            config={"username": os.environ["GMAIL_USER"], "password": os.environ["GMAIL_PASSWORD"], "timeout": 3},
        )
        GMailDispatcher(ch).send("test@example.com", mail_payload)
        mock.assert_called()
        s: Mock = mock.return_value
        s.login.assert_called()
        s.starttls.assert_called()
        s.sendmail.assert_called()
        s.sendmail.assert_called_with(from_addr=os.environ["GMAIL_USER"], to_addrs=["test@example.com"], msg=ANY)


def test_config() -> None:
    d: GMailDispatcher = GMailDispatcher(Mock(config={}))
    with pytest.raises(ValidationError):
        d.config


@pytest.mark.parametrize(
    "newsletter, page_size, addresses, expected",
    pytest.param(False, None, "a@b.com", "a@b.com"),
    pytest.param(False, 2, ["a1@b.com", "a2@b.com", "a3@b.com"], [["a1@b.com", "a2@b.com"], "a3@b.com"]], ),
    pytest.param(False, 3, ["a1@b.com", "a2@b.com", "a3@b.com"], [["a1@b.com", "a2@b.com", "a3@b.com"]], ),
)
def test_gmail_newsletter(occurrence: "Occurrence", mocked_responses: "RequestsMock", monkeypatch: "MonkeyPatch") -> None:
    from bitcaster.dispatchers import GMailDispatcher
    from bitcaster.models import Channel, Project

    with patch("smtplib.SMTP", autospec=True) as mock:
        ch = Channel(
            project=Project(from_email=os.environ["GMAIL_USER"], subject_prefix="[gmail] "),
            config={"username": os.environ["GMAIL_USER"], "password": os.environ["GMAIL_PASSWORD"], "timeout": 3},
        )
        GMailDispatcher(ch).send("test@example.com", mail_payload)
        mock.assert_called()
        s: Mock = mock.return_value
        s.login.assert_called()
        s.starttls.assert_called()
        s.sendmail.assert_called()
        s.sendmail.assert_called_with(from_addr=os.environ["GMAIL_USER"], to_addrs=["test@example.com"], msg=ANY)
