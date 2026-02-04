from django import forms

from bitcaster.models import Attachment


class AttachmentForm(forms.ModelForm[Attachment]):
    class Meta:
        model = Attachment
        fields = ("document", "mime_type")
