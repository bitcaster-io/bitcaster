import os
from pathlib import Path

from responses import RequestsMock

import pytest
from unittest.mock import Mock

from django.core.exceptions import ValidationError
from strategy_field.utils import fqn

from bitcaster.dispatchers import MailJetDispatcher
from bitcaster.dispatchers.base import Payload
from bitcaster.exceptions import DispatcherError

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


@pytest.mark.parametrize("status_code", [401, 403])
def test_mailjet_error(
    monkeypatch: pytest.MonkeyPatch, mail_payload: Payload, mocked_responses: RequestsMock, status_code: int
) -> None:
    from bitcaster.dispatchers import MailJetDispatcher
    from bitcaster.models import Channel, Project

    mocked_responses.add(mocked_responses.POST, "https://api.mailjet.com/v3.1/send", "{}", status=status_code)

    ch = Channel(
        project=Project(from_email="", subject_prefix="[mailjet] "),
        dispatcher=fqn(MailJetDispatcher),
        config={
            "api_key": "key",
            "secret_key": "secret",
            "from_address": "sender@bitcaster.io",
            "from_label": "Bitcaster",
        },
    )
    with pytest.raises(DispatcherError):
        MailJetDispatcher(ch).send("sender@bitcaster.io", mail_payload)


def test_config() -> None:
    d: MailJetDispatcher = MailJetDispatcher(Mock(config={}))
    with pytest.raises(ValidationError):
        _ = d.config


def test_mailjet_no_from_label(mail_payload: Payload, mocked_responses: RequestsMock) -> None:
    from bitcaster.dispatchers import MailJetDispatcher
    from bitcaster.models import Channel, Project

    mocked_responses._add_from_file(file_path=RESPONSE_FIXTURE)

    ch = Channel(
        project=Project(from_email="sender@bitcaster.io", subject_prefix="[mailjet] "),
        dispatcher=fqn(MailJetDispatcher),
        config={
            "api_key": "key",
            "secret_key": "secret",
            "from_address": "sender@bitcaster.io",
            "from_label": "",
        },
    )
    MailJetDispatcher(ch).send("recipient@example.com", mail_payload)
