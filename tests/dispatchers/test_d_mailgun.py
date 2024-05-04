import os
from pathlib import Path
from unittest.mock import Mock

import pytest
from django.core.exceptions import ValidationError

from bitcaster.dispatchers import MailgunDispatcher

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


@pytest.mark.parametrize("mail_payload", ("", "html_message"), indirect=True)
def test_mailgun(monkeypatch, mail_payload, mocked_responses):
    from bitcaster.dispatchers import MailgunDispatcher
    from bitcaster.models import Application, Channel

    mocked_responses._add_from_file(file_path=Path(__file__).parent / "mailgun.yaml")

    ch = Channel(
        application=Application(from_email=os.environ["TEST_EMAIL_SENDER"], subject_prefix="[mailgun] "),
        config={"api_key": os.environ["MAILGUN_API_KEY"], "sender_domain": os.environ["MAILGUN_SENDER_DOMAIN"]},
    )
    MailgunDispatcher(ch).send(os.environ["TEST_EMAIL_RECIPIENT"], mail_payload)


def test_config():
    d: MailgunDispatcher = MailgunDispatcher(Mock(config={}))
    with pytest.raises(ValidationError):
        d.config
