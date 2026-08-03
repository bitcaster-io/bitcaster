from typing import TYPE_CHECKING, Any, cast

from unfold.widgets import UnfoldAdminSelect2MultipleWidget

from django import forms
from django.utils.translation import gettext_lazy as _
from django_svelte_jsoneditor.widgets import SvelteJSONEditorWidget

from bitcaster.models import Channel, Event

from .unfold import UnfoldForm

if TYPE_CHECKING:
    from bitcaster.models.occurrence import OccurrenceOptions


def _depth_choices() -> "list[tuple[str, str]]":
    return [
        ("fast", "Fast"),
        ("full", "Full"),
        ("partial", "Partial"),
    ]


API_PAYLOAD_SKELETON: "dict[str, Any]" = {
    "payload_context": {"foo": "bar"},
    "options": {"limit_to": [], "channels": [], "environs": [], "filters": {}},
}


class EventBaseForm(forms.ModelForm["Event"]):
    class Meta:
        model = Event
        exclude = ("config", "locked")  # noqa: DJ006


class EventAddForm(EventBaseForm):
    class Meta:
        model = Event
        exclude = ("channels", "locked")  # noqa: DJ006


class EventChangeForm(EventBaseForm):
    class Meta:
        model = Event
        exclude = ()  # noqa: DJ006


class EventDebugForm(UnfoldForm):
    mode = forms.ChoiceField(
        choices=_depth_choices,
        initial="fast",
        label="Depth",
        help_text=_(
            "fast - deliveries only, no rendered content; "
            "full - render all message templates; "
            "partial - render only the first N recipients (see DEBUG_PREVIEW_RENDER_LIMIT)"
        ),
    )
    context = forms.JSONField(
        widget=SvelteJSONEditorWidget(),
        required=False,
        label="Context",
        help_text=_("Context data passed to the notification templates. Leave empty ({}) to use an empty context."),
    )
    api_payload = forms.JSONField(
        widget=SvelteJSONEditorWidget(),
        required=False,
        label=_("Emulate API call"),
        help_text=_(
            "Paste the JSON body sent to the trigger endpoint, "
            'e.g. {"payload_context": {"foo": "bar"}, "options": {"limit_to": ["a@example.com"]}}. '
            "If present, it overrides Context and the options below."
        ),
    )
    limit_to = forms.CharField(
        required=False,
        label="Limit to",
        help_text=_(
            "Restrict delivery to these registered addresses (space or comma separated). "
            "Leave empty to deliver to all subscribers of the event."
        ),
    )
    channels = forms.ModelMultipleChoiceField(
        queryset=Channel.objects.none(),
        required=False,
        widget=UnfoldAdminSelect2MultipleWidget,
        help_text=_("Channels used to deliver the notification. Leave empty to use all active channels of the event."),
    )

    def __init__(self, *args: Any, **kwargs: Any):
        self.event = kwargs.pop("event", None)
        super().__init__(*args, **kwargs)
        if self.event:
            self.fields["channels"].queryset = self.event.channels.filter(active=True, locked=False, paused=False)

    def clean_limit_to(self) -> str | None:
        from bitcaster.models import Address

        value = self.cleaned_data["limit_to"]
        if not value:
            return None
        entries = [entry.strip() for entry in value.replace(",", " ").split() if entry.strip()]
        if not entries:
            return None
        known = set(Address.objects.filter(value__in=entries).values_list("value", flat=True))
        unknown = [entry for entry in entries if entry not in known]
        if unknown:
            raise forms.ValidationError(
                _("Unknown address(es): %(addresses)s. Limit to only accepts registered addresses.")
                % {"addresses": ", ".join(unknown)}
            )
        return " ".join(entries)

    def clean(self) -> dict[str, Any]:
        super().clean()
        payload = self.cleaned_data.get("api_payload") or {}
        if payload and payload != API_PAYLOAD_SKELETON:
            options = payload.get("options") or {}
            unknown = set(options) - {"limit_to", "channels", "environs", "filters"}
            if unknown:
                raise forms.ValidationError(_("Unknown option(s): %(fields)s") % {"fields": ", ".join(sorted(unknown))})
            payload_context = payload.get("payload_context", payload.get("context"))
            if payload_context is None:
                payload_context = {}
            if not isinstance(payload_context, dict):
                raise forms.ValidationError(_("payload_context must be a JSON object"))
            if channels := options.get("channels"):
                allowed = set(
                    self.event.channels.filter(active=True, locked=False, paused=False).values_list("pk", flat=True)
                )
                requested = {int(c) for c in channels if str(c).isdigit()}
                unknown_channels = requested - allowed
                if unknown_channels:
                    raise forms.ValidationError(
                        _("Channel(s) not enabled for this event: %(channels)s")
                        % {"channels": ", ".join(str(c) for c in sorted(unknown_channels))}
                    )
            self.cleaned_data["context"] = payload_context
            self.cleaned_data["_emulated_options"] = options
        return self.cleaned_data

    def get_options(self) -> "OccurrenceOptions":
        if emulated := self.cleaned_data.get("_emulated_options"):
            emulated_options = dict(emulated)
            if channels := emulated_options.get("channels"):
                emulated_options["channels"] = [int(c) for c in channels if str(c).isdigit()]
            return cast("OccurrenceOptions", emulated_options)
        options: "OccurrenceOptions" = {}
        if limit_to := self.cleaned_data.get("limit_to"):
            entries = [entry.strip() for entry in limit_to.replace(",", " ").split() if entry.strip()]
            if entries:
                options["limit_to"] = entries
        if channels := self.cleaned_data.get("channels"):
            options["channels"] = [channel.pk for channel in channels]
        return options
