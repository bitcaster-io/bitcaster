import os
from typing import List, TYPE_CHECKING
from unittest.mock import ANY, Mock, patch

import pytest
from django.core.exceptions import ValidationError
from responses import RequestsMock

from bitcaster.dispatchers import GMailDispatcher

if TYPE_CHECKING:
    from bitcaster.dispatchers.base import Payload

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


@pytest.mark.parametrize(
    "mail_payload, recipients_list",
    (
        ("", 1),
        ("html_message", 1),
        ("", 2),
        ("html_message", 2),
    ),
    indirect=True,
)
def test_gmail(mocked_responses: "RequestsMock", mail_payload: "Payload", recipients_list: str | List[str]) -> None:
    from bitcaster.dispatchers import GMailDispatcher
    from bitcaster.models import Channel, Project

    with patch("smtplib.SMTP", autospec=True) as mock:
        ch = Channel(
            project=Project(from_email=os.environ["GMAIL_USER"], subject_prefix="[gmail] "),
            config={"username": os.environ["GMAIL_USER"], "password": os.environ["GMAIL_PASSWORD"], "timeout": 3},
        )
        if isinstance(recipients_list, str):
            GMailDispatcher(ch).send(recipients_list, mail_payload)
        else:
            GMailDispatcher(ch).send_many(recipients_list, mail_payload)
        mock.assert_called()
        s: Mock = mock.return_value
        s.login.assert_called()
        s.starttls.assert_called()
        s.sendmail.assert_called()
        if isinstance(recipients_list, str):
            recipients_list = [recipients_list]
        s.sendmail.assert_called_with(from_addr=os.environ["GMAIL_USER"], to_addrs=recipients_list, msg=ANY)


def test_config() -> None:
    d: GMailDispatcher = GMailDispatcher(Mock(config={}))
    with pytest.raises(ValidationError):
        d.config
