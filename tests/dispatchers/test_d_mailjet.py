import os
from pathlib import Path
from unittest.mock import Mock

import pytest
from django.core.exceptions import ValidationError
from responses import RequestsMock
from strategy_field.utils import fqn

from bitcaster.dispatchers import MailJetDispatcher
from bitcaster.dispatchers.base import Payload

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]

RESPONSE_FIXTURE = Path(__file__).parent / "mailjet.yaml"


# @_recorder.record(file_path=RESPONSE_FIXTURE)
def test_mailjet(monkeypatch: pytest.MonkeyPatch, mail_payload: Payload, mocked_responses: RequestsMock) -> None:
    from bitcaster.dispatchers import MailJetDispatcher
    from bitcaster.models import Channel, Project

    if "MAILJET_SENDER" in os.environ:
        mocked_responses.passthru_prefixes = (r"https://api.mailjet.com/",)
    else:
        mocked_responses._add_from_file(file_path=RESPONSE_FIXTURE)
        os.environ.setdefault("MAILJET_SENDER", "sender@bitcaster.io")
        os.environ.setdefault("MAILJET_RCPT", "recipient@bitcaster.io")
        os.environ.setdefault("MAILJET_API_KEY", "key")
        os.environ.setdefault("MAILJET_API_SECRET", "secret")

    ch = Channel(
        project=Project(from_email=os.environ["MAILJET_SENDER"], subject_prefix="[mailjet] "),
        dispatcher=fqn(MailJetDispatcher),
        config={
            "api_key": os.environ["MAILJET_API_KEY"],
            "secret_key": os.environ["MAILJET_API_SECRET"],
            "from_address": os.environ["MAILJET_SENDER"],
            "from_label": "Bitcaster",
        },
    )
    MailJetDispatcher(ch).send(os.environ["TEST_EMAIL_RECIPIENT"], mail_payload)


def test_config() -> None:
    d: MailJetDispatcher = MailJetDispatcher(Mock(config={}))
    with pytest.raises(ValidationError):
        _ = d.config
