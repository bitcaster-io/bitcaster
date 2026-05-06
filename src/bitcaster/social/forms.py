from typing import Any

from unfold.widgets import UnfoldAdminTextInputWidget

from django import forms
from django.db.models import Model
from django.utils.translation import gettext_lazy as _

from .models import SocialProvider


class WriteOnlyWidget(UnfoldAdminTextInputWidget):
    template_name = "unfold/write_only.html"
    MASK = "***"

    def format_value(self, value: Any) -> str:
        if value:
            return self.MASK
        return ""


class WriteOnlyFieldMixin(forms.ModelForm[Model]):
    write_only_fields = ["secret", "key"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for f in self.write_only_fields:
            if getattr(self.instance, f):
                self.fields[f].help_text = _("Leave '%s' to keep the existing value." % WriteOnlyWidget.MASK)
                self.fields[f].widget = WriteOnlyWidget(attrs={"suffix": "set"})
                self.fields[f].required = False
            else:
                self.fields[f].help_text = _("Write only. Once set it cannot be read")
                self.fields[f].widget = WriteOnlyWidget(attrs={"suffix": "not set"})

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean() or {}
        for f in self.write_only_fields:
            if cleaned_data.get(f) == WriteOnlyWidget.MASK:
                cleaned_data[f] = getattr(self.instance, f)
        return cleaned_data


class SocialProviderForm(WriteOnlyFieldMixin, forms.ModelForm["SocialProvider"]):
    class Meta:
        model = SocialProvider
        fields = ["label", "provider", "enabled", "client_id", "secret", "key", "configuration"]

    def clean(self) -> Any:
        cleaned_data = super().clean()
        provider = cleaned_data.get("provider")
        qs = SocialProvider.objects.filter(provider=provider)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError({"provider": _("A configuration for this provider already exists.")})

        return cleaned_data
