from django import forms
from django.contrib import admin

from bitcaster.constants import Bitcaster
from bitcaster.models import Notification, Organization

from .fields import Select2TagField
from .widgets import AutocompletSelectEnh


class NotificationForm(forms.ModelForm["Notification"]):
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.exclude(name=Bitcaster.ORGANIZATION),
        required=True,
        widget=AutocompletSelectEnh(
            Notification._meta.get_field("event"),
            admin.site,
            exclude={"name": Bitcaster.ORGANIZATION},
        ),
    )
    environments = Select2TagField(required=False)

    class Meta:
        model = Notification
        exclude = ("config", "locked")
