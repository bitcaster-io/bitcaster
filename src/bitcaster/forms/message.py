from typing import Any

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django_svelte_jsoneditor.widgets import SvelteJSONEditorWidget
from tinymce.widgets import TinyMCE

from bitcaster.models import Channel, Event, Message, Notification, Organization
from bitcaster.web import widgets


class MessageEditForm(forms.ModelForm[Message]):
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
        css = {"screen": ["tinymce/skins/ui/oxide/skin.min.css", "css/unfold.css"]}
        return orig + forms.Media(js=js, css=css)  # type: ignore

    class Meta:
        model = Message
        fields = ("subject", "content", "html_content", "context", "recipient")


class MessageRenderForm(MessageEditForm):
    content_type = forms.CharField(widget=forms.HiddenInput)


class MessageChangeForm(forms.ModelForm[Message]):
    class Meta:
        model = Message
        fields = ("name", "channel", "notification")


class MessageCreationForm(forms.ModelForm[Message]):
    organization = forms.ModelChoiceField(queryset=Organization.objects.all(), widget=forms.HiddenInput, required=False)
    event = forms.ModelChoiceField(queryset=Event.objects.all(), widget=forms.HiddenInput, required=False)
    notification = forms.ModelChoiceField(
        queryset=Notification.objects.all(),
        required=True,
        widget=AutocompleteSelect(Message._meta.get_field("notification"), admin.site),
    )

    class Meta:
        model = Message
        fields = ("name", "channel", "notification")

    def clean(self) -> None:
        super().clean()
        if "channel" in self.cleaned_data and "notification" in self.cleaned_data:
            self.cleaned_data["organization"] = self.cleaned_data["channel"].organization


class NotificationTemplateCreateForm(forms.Form):
    name = forms.CharField(widget=widgets.UnfoldAdminTextInputWidget(attrs={"placeholder": "Name"}))
    channel = forms.ModelChoiceField(
        queryset=Channel.objects.all(), label="Channel", widget=widgets.UnfoldAdminSelectWidget
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
