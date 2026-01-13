from typing import Any

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_svelte_jsoneditor.widgets import SvelteJSONEditorWidget
from tinymce.widgets import TinyMCE

from bitcaster.models import Channel, Event, MessageTemplate, Notification, Organization

from . import unfold

# from .unfold import UnfoldForm, UnfoldAdminSelect2Widget, UnfoldAdminTextInputWidget,


class MessageTemplateCloneForm(forms.ModelForm[MessageTemplate]):
    name = forms.CharField()
    event = forms.ModelChoiceField(Event.objects.all(), widget=unfold.UnfoldAdminSelect2Widget)
    channel = forms.ModelChoiceField(Channel.objects.all(), widget=unfold.UnfoldAdminSelect2Widget)

    class Meta:
        model = MessageTemplate
        fields = ("name", "event", "channel")


class MessageTemplateEditForm(forms.ModelForm[MessageTemplate]):
    recipient = forms.CharField(required=False)
    subject = forms.CharField(required=False)
    content = forms.CharField(widget=forms.Textarea, required=False)
    html_content = forms.CharField(
        required=False, widget=TinyMCE(mce_attrs={"setup": "setupTinyMCE", "height": "400px"})
    )
    context = forms.JSONField(widget=SvelteJSONEditorWidget(), required=False)

    @property
    def media(self) -> forms.Media:
        orig = super().media
        extra = "" if settings.DEBUG else ".min"
        js = [
            "admin/js/vendor/jquery/jquery%s.js" % extra,
            "admin/js/jquery.init.js",
            "bitcaster/js/editor%s.js" % extra,
        ]
        css = {
            "screen": [
                "tinymce/skins/ui/oxide/skin.min.css",
                "css/message_editor.css",
            ]
        }
        return orig + forms.Media(js=js, css=css)  # type: ignore

    class Meta:
        model = MessageTemplate
        fields = ("subject", "content", "html_content", "context", "recipient")


class MessageTemplateRenderForm(MessageTemplateEditForm):
    content_type = forms.CharField(widget=forms.HiddenInput)


def validate_cleaned_data(form: "forms.ModelForm[MessageTemplate] | NotificationTemplateCreateForm") -> None:
    if "channel" in form.cleaned_data and "notification" in form.cleaned_data:
        form.cleaned_data["organization"] = form.cleaned_data["channel"].organization
    if (
        "channel" in form.cleaned_data
        and "event" in form.cleaned_data
        and (form.cleaned_data["channel"] not in form.cleaned_data["event"].channels.all())
    ):
        form.add_error("channel", _("This channel is not available for the selected event"))


class MessageTemplateChangeForm(forms.ModelForm[MessageTemplate]):
    class Meta:
        model = MessageTemplate
        fields = ("name", "event", "channel", "notification", "debug")

    def clean(self) -> None:
        super().clean()
        validate_cleaned_data(self)


class MessageTemplateCreationForm(forms.ModelForm[MessageTemplate]):
    organization = forms.ModelChoiceField(queryset=Organization.objects.all(), widget=forms.HiddenInput, required=False)
    event = forms.ModelChoiceField(
        queryset=Event.objects.all(),
        required=True,
        widget=unfold.UnfoldAdminSelect2Widget,
    )
    notification = forms.ModelChoiceField(
        queryset=Notification.objects.all(),
        required=False,
        widget=unfold.UnfoldAdminSelect2Widget,
    )

    class Meta:
        model = MessageTemplate
        fields = ("name", "event", "channel", "notification")

    def clean(self) -> None:
        super().clean()
        validate_cleaned_data(self)


class NotificationTemplateCreateForm(forms.Form):
    name = forms.CharField(widget=unfold.UnfoldAdminTextInputWidget(attrs={"placeholder": "Name"}))
    channel = forms.ModelChoiceField(
        queryset=Channel.objects.all(), label="Channel", widget=unfold.UnfoldAdminSelectWidget
    )

    notification: "Notification"

    def __init__(self, *args: Any, **kwargs: Any):
        self.notification = kwargs.pop("notification")
        super().__init__(*args, **kwargs)
        self.fields["channel"].queryset = self.notification.event.channels.all()

    def clean_name(self) -> str:
        name = self.cleaned_data["name"]
        if self.notification.messages.filter(name__iexact=name).exists():
            raise ValidationError(_("This name is already in use."))
        return name

    def clean(self) -> None:
        super().clean()
        validate_cleaned_data(self)
