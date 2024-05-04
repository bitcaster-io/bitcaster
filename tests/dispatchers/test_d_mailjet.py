import os
from pathlib import Path
from unittest.mock import Mock

import pytest
from django.core.exceptions import ValidationError

from bitcaster.dispatchers import MailJetDispatcher

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


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


def test_config():
    d: MailJetDispatcher = MailJetDispatcher(Mock(config={}))
    with pytest.raises(ValidationError):
        d.config
