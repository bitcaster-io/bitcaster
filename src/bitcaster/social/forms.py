from typing import TYPE_CHECKING

from django import forms

from .models import SocialProvider

if TYPE_CHECKING:
    SocialProviderForm = "SocialProviderUpdateForm | SocialProviderAddForm"


class SocialProviderUpdateForm(forms.ModelForm["SocialProvider"]):
    class Meta:
        model = SocialProvider
        fields = ["label", "provider", "enabled", "configuration"]


class SocialProviderAddForm(forms.ModelForm["SocialProvider"]):
    class Meta:
        model = SocialProvider
        fields = ["label", "provider", "enabled"]
