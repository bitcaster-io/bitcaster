from typing import TYPE_CHECKING, Any

from unfold.widgets import UnfoldAdminSelect2MultipleWidget

from django import forms
from django_svelte_jsoneditor.widgets import SvelteJSONEditorWidget

from bitcaster.models import Channel, Event

from .unfold import UnfoldAdminSelectWidget, UnfoldForm

if TYPE_CHECKING:
    from bitcaster.models.occurrence import OccurrenceOptions


def _depth_choices() -> "list[tuple[str, str]]":
    return [
        ("fast", "Fast"),
        ("full", "Full"),
        ("partial", "Partial"),
    ]


def _execution_choices() -> "list[tuple[str, str]]":
    return [
        ("sync", "Sync"),
        ("background", "Background"),
    ]


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
    mode = forms.ChoiceField(choices=_depth_choices, initial="fast", label="Depth")
    context = forms.JSONField(widget=SvelteJSONEditorWidget(), required=False)
    limit_to = forms.CharField(required=False, label="Limit to")
    channels = forms.ModelMultipleChoiceField(
        queryset=Channel.objects.none(), required=False, widget=UnfoldAdminSelect2MultipleWidget
    )
    execution = forms.ChoiceField(choices=_execution_choices, initial="sync", widget=UnfoldAdminSelectWidget)

    def __init__(self, *args: Any, **kwargs: Any):
        self.event = kwargs.pop("event", None)
        super().__init__(*args, **kwargs)
        if self.event:
            self.fields["channels"].queryset = self.event.channels.all()

    def clean_limit_to(self) -> str | None:
        value = self.cleaned_data["limit_to"]
        if not value:
            return None
        return value.strip() or None

    def get_options(self) -> "OccurrenceOptions":
        options: "OccurrenceOptions" = {}
        if limit_to := self.cleaned_data.get("limit_to"):
            entries = [entry.strip() for entry in limit_to.replace(",", " ").split() if entry.strip()]
            if entries:
                options["limit_to"] = entries
        if channels := self.cleaned_data.get("channels"):
            options["channels"] = [channel.pk for channel in channels]
        return options
