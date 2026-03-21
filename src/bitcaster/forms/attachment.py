import mimetypes

from django import forms

from bitcaster.models import Attachment

mimetypes.init()


class AttachmentForm(forms.ModelForm[Attachment]):
    class Meta:
        model = Attachment
        fields = (
            "application",
            "document",
            "filename",
            "correlation_id",
            "mime_type",
        )

    def clean(self) -> dict[str, str | None]:
        super().clean()
        if not self.cleaned_data.get("mime_type"):
            self.cleaned_data["mime_type"] = mimetypes.guess_type(self.cleaned_data["document"].name)[0]
        if not self.cleaned_data.get("filename"):
            self.cleaned_data["filename"] = self.cleaned_data["document"].name
        return self.cleaned_data
