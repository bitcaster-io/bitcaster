from typing import TYPE_CHECKING

import pytest
from constance.test.pytest import override_config
from django import template
from testutils.factories.attachment import AttachmentFactory
from testutils.factories.event import EventFactory
from testutils.factories.org import ApplicationFactory

from bitcaster.dispatchers.base import Capability
from bitcaster.web.templatetags.attachments import UnrelatedEventError
from bitcaster.web.templatetags.attachments import attachment as attachment_tag
from bitcaster.web.templatetags.protocols import has

if TYPE_CHECKING:
    from bitcaster.models import Channel


def test_has(channel: "Channel") -> None:
    assert has(channel, Capability.TEXT)


@pytest.mark.parametrize(
    "validity",
    [
        pytest.param(None, id="none-perpetual"),
        pytest.param(0, id="zero-perpetual"),
        pytest.param(1500, id="ttl"),
    ],
)
@override_config(SERVER_URL="https://example.com")
def test_attachment_returns_a_url(validity):
    attachment = AttachmentFactory()
    event = EventFactory(application=attachment.application)

    mock_context = template.Context({"event": event, "validity": validity, "address": ""})

    assert attachment_tag(mock_context, attachment.correlation_id).startswith(
        "https://example.com/attachment/download/"
    )


def test_attachment_raises_with_negative_validity():
    attachment = AttachmentFactory()
    event = EventFactory(application=attachment.application)

    mock_context = template.Context({"event": event, "validity": -1, "address": ""})

    with pytest.raises(ValueError, match="attachment: TTL must be an integer"):
        attachment_tag(mock_context, attachment.correlation_id, "aa")


def test_attachment_raises_with_unrelated_attachment():
    application = ApplicationFactory(name="Attach here")
    attachment = AttachmentFactory(application=application)
    unrelated_application = ApplicationFactory(name="Wrong app")
    unrelated_event = EventFactory(application=unrelated_application)

    mock_context = template.Context({"event": unrelated_event, "validity": None, "address": ""})

    with pytest.raises(UnrelatedEventError):
        attachment_tag(mock_context, attachment.correlation_id)
