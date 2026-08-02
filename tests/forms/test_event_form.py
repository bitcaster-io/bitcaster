from typing import TYPE_CHECKING

import pytest
from testutils.factories import AddressFactory, AssignmentFactory, EventFactory

from bitcaster.forms.event import EventDebugForm

if TYPE_CHECKING:
    from bitcaster.models import Event

pytestmark = [pytest.mark.forms, pytest.mark.django_db]


def test_debug_form_builds_options_with_limit_to_and_channels() -> None:
    event: "Event" = EventFactory(channels=[AssignmentFactory().channel])
    channels = list(event.channels.all())
    AddressFactory(value="a@example.com")
    AddressFactory(value="b@example.com")
    AddressFactory(value="c@example.com")
    form = EventDebugForm(
        event=event,
        data={
            "context": '{"foo": "bar"}',
            "mode": "full",
            "limit_to": "a@example.com, b@example.com c@example.com",
            "channels": [channels[0].pk],
        },
    )
    assert form.is_valid()

    options = form.get_options()
    assert options["limit_to"] == ["a@example.com", "b@example.com", "c@example.com"]
    assert options["channels"] == [channels[0].pk]


def test_debug_form_clean_limit_to_strips_value() -> None:
    AddressFactory(value="a@example.com")
    AddressFactory(value="b@example.com")
    form = EventDebugForm(data={"limit_to": "  a@example.com, b@example.com  ", "mode": "fast"})
    assert form.is_valid()
    assert form.cleaned_data["limit_to"].startswith("a@example.com")
    assert form.cleaned_data["limit_to"].endswith("b@example.com")


def test_debug_form_rejects_unknown_limit_to_address() -> None:
    AddressFactory(value="a@example.com")
    form = EventDebugForm(data={"limit_to": "a@example.com, ghost@example.com", "mode": "fast"})
    assert not form.is_valid()
    assert "ghost@example.com" in form.errors["limit_to"][0]


def test_debug_form_empty_limit_to_no_options() -> None:
    form = EventDebugForm(data={"mode": "fast"})
    assert form.is_valid()
    assert form.get_options().get("limit_to") is None


def test_debug_form_separators_only_limit_to_is_none() -> None:
    form = EventDebugForm(data={"limit_to": ", ,, ", "mode": "fast"})
    assert form.is_valid()
    assert form.cleaned_data["limit_to"] is None
    assert form.get_options().get("limit_to") is None


def test_debug_form_emulates_api_payload() -> None:
    event: "Event" = EventFactory(channels=[AssignmentFactory().channel])
    channel = event.channels.first()
    payload = '{"payload_context": {"foo": "bar"}, "options": {"limit_to": ["a@example.com"], "channels": ["%s"]}}'
    form = EventDebugForm(
        event=event,
        data={"mode": "fast", "api_payload": payload % channel.pk},
    )
    assert form.is_valid()
    assert form.cleaned_data["context"] == {"foo": "bar"}
    options = form.get_options()
    assert options["limit_to"] == ["a@example.com"]
    assert options["channels"] == [channel.pk]


def test_debug_form_emulates_api_payload_with_context_alias() -> None:
    event: "Event" = EventFactory(channels=[AssignmentFactory().channel])
    form = EventDebugForm(
        event=event,
        data={"mode": "fast", "api_payload": '{"context": {"foo": "bar"}}'},
    )
    assert form.is_valid()
    assert form.cleaned_data["context"] == {"foo": "bar"}
    assert form.get_options() == {}


def test_debug_form_emulation_rejects_unknown_option() -> None:
    event: "Event" = EventFactory(channels=[AssignmentFactory().channel])
    form = EventDebugForm(
        event=event,
        data={"mode": "fast", "api_payload": '{"options": {"bogus": 1}}'},
    )
    assert not form.is_valid()
    assert "bogus" in form.errors["__all__"][0]


def test_debug_form_emulation_rejects_non_event_channel() -> None:
    from testutils.factories import ChannelFactory

    event: "Event" = EventFactory(channels=[AssignmentFactory().channel])
    other = ChannelFactory()
    form = EventDebugForm(
        event=event,
        data={
            "mode": "fast",
            "api_payload": '{"payload_context": {}, "options": {"channels": ["%s"]}}' % other.pk,
        },
    )
    assert not form.is_valid()
    assert "not enabled for this event" in form.errors["__all__"][0]


def test_debug_form_emulation_rejects_non_object_context() -> None:
    event: "Event" = EventFactory(channels=[AssignmentFactory().channel])
    form = EventDebugForm(
        event=event,
        data={"mode": "fast", "api_payload": '{"payload_context": [1, 2]}'},
    )
    assert not form.is_valid()
    assert "must be a JSON object" in form.errors["__all__"][0]


def test_debug_form_only_offers_event_enabled_channels() -> None:
    from testutils.factories import ChannelFactory

    event: "Event" = EventFactory(channels=[AssignmentFactory().channel])
    enabled = event.channels.first()
    disabled = ChannelFactory(active=False)
    event.channels.add(disabled)
    form = EventDebugForm(event=event)
    pks = {c.pk for c in form.fields["channels"].queryset}
    assert enabled.pk in pks
    assert disabled.pk not in pks


def test_unfold_form_upgrades_plain_multiple_widget() -> None:
    from django import forms

    from bitcaster.forms.unfold import UnfoldForm

    class PlainMultipleForm(UnfoldForm):
        def items_choices(self) -> list[tuple[str, str]]:
            return [("a", "A"), ("b", "B")]

        items = forms.MultipleChoiceField(choices=items_choices)

    form = PlainMultipleForm()
    assert form.is_valid() is False
    assert isinstance(form.fields["items"].widget, forms.SelectMultiple)
