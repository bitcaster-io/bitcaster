from typing import TYPE_CHECKING

import pytest
from testutils.factories import AssignmentFactory, EventFactory

from bitcaster.forms.event import EventDebugForm

if TYPE_CHECKING:
    from bitcaster.models import Event

pytestmark = [pytest.mark.forms, pytest.mark.django_db]


def test_debug_form_builds_options_with_limit_to_and_channels() -> None:
    event: "Event" = EventFactory(channels=[AssignmentFactory().channel])
    channels = list(event.channels.all())
    form = EventDebugForm(
        event=event,
        data={
            "context": '{"foo": "bar"}',
            "mode": "full",
            "limit_to": "a@example.com, b@example.com c@example.com",
            "channels": [channels[0].pk],
            "execution": "sync",
        },
    )
    assert form.is_valid()

    options = form.get_options()
    assert options["limit_to"] == ["a@example.com", "b@example.com", "c@example.com"]
    assert options["channels"] == [channels[0].pk]


def test_debug_form_clean_limit_to_strips_value() -> None:
    form = EventDebugForm(data={"limit_to": "  a@example.com, b@example.com  ", "mode": "fast", "execution": "sync"})
    assert form.is_valid()
    assert form.cleaned_data["limit_to"].startswith("a@example.com")
    assert form.cleaned_data["limit_to"].endswith("b@example.com")


def test_debug_form_empty_limit_to_no_options() -> None:
    form = EventDebugForm(data={"mode": "fast", "execution": "sync"})
    assert form.is_valid()
    assert form.get_options().get("limit_to") is None
