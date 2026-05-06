from typing import TYPE_CHECKING, TypedDict

from constance.test.pytest import override_config

import pytest
from testutils.factories.attachment import AttachmentFactory
from testutils.factories.event import EventFactory
from testutils.factories.org import ApplicationFactory

from django import template

from bitcaster.web.templatetags.attachments import UnrelatedEventError, attachment as attachment_tag

if TYPE_CHECKING:
    from bitcaster.models import Application, Attachment, Event

    Context = TypedDict(
        "Context",
        {
            "attachment": Attachment,
            "event": Event,
            "application": Application,
            "unrelated_event": Event,
        },
    )


@pytest.fixture
def data() -> "Context":
    attachment = AttachmentFactory.create()
    return {
        "attachment": attachment,
        "event": EventFactory.create(application=attachment.application),
        "application": ApplicationFactory.create(name="Attach here"),
        "unrelated_event": EventFactory.create(application__name="Unrelated Application"),
    }


@pytest.mark.parametrize(
    "validity",
    [
        pytest.param(None, id="none-perpetual"),
        pytest.param(0, id="zero-perpetual"),
        pytest.param(1500, id="ttl"),
    ],
)
@override_config(SERVER_URL="https://example.com")
def test_attachment_returns_a_url(validity, data: "Context") -> None:
    attachment = data["attachment"]
    event = data["event"]

    mock_context = template.Context({"event": event, "validity": validity, "address": ""})

    assert attachment_tag(mock_context, attachment.correlation_id).startswith(
        "https://example.com/attachment/download/"
    )


def test_attachment_raises_with_negative_validity(data: "Context") -> None:
    attachment = data["attachment"]
    event = data["event"]

    mock_context = template.Context({"event": event, "validity": -1, "address": ""})

    with pytest.raises(ValueError, match="attachment: TTL must be an integer"):
        attachment_tag(mock_context, attachment.correlation_id, "aa")


def test_attachment_raises_with_unrelated_attachment(data: "Context") -> None:
    unrelated_event = data["unrelated_event"]
    attachment = data["attachment"]
    mock_context = template.Context({"event": unrelated_event, "validity": None, "address": ""})

    with pytest.raises(UnrelatedEventError):
        attachment_tag(mock_context, attachment.correlation_id)
