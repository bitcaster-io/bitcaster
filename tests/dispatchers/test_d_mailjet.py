import os
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest
from django.core.exceptions import ValidationError
from responses import RequestsMock

from bitcaster.dispatchers import MailJetDispatcher
from bitcaster.dispatchers.base import Payload

if TYPE_CHECKING:
    from pytest import MonkeyPatch

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


# @_recorder.record(file_path=Path(__file__).parent / "mailjet.yaml")
def test_mailjet(monkeypatch: "MonkeyPatch", mail_payload: Payload, mocked_responses: RequestsMock) -> None:
    from bitcaster.dispatchers import MailJetDispatcher
    from bitcaster.models import Channel, Project

    mocked_responses._add_from_file(file_path=Path(__file__).parent / "mailjet.yaml")

    ch = Channel(
        project=Project(from_email=os.environ["GMAIL_USER"], subject_prefix="[gmail] "),
        config={"api_key": os.environ["MAILJET_API_KEY"], "secret_key": os.environ["MAILJET_SECRET_KEY"]},
    )

    MailJetDispatcher(ch).send(os.environ["TEST_EMAIL_RECIPIENT"], mail_payload)


def test_config() -> None:
    d: MailJetDispatcher = MailJetDispatcher(Mock(config={}))
    with pytest.raises(ValidationError):
        d.config
