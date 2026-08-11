from typing import Any

from django import forms
from django.utils.translation import gettext_lazy as _

from bitcaster.models import Subscription


class SubscriptionForm(forms.ModelForm["Subscription"]):
    def clean(self) -> dict[str, Any]:
        cleaned: dict[str, Any] = super().clean() or {}
        notification = cleaned.get("notification")
        assignment = cleaned.get("assignment")
        if notification and assignment:
            queryset = Subscription.objects.filter(notification=notification, assignment=assignment)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError(_("A subscription for this notification and assignment already exists."))
        return cleaned

    class Meta:
        model = Subscription
        fields = ("notification", "assignment", "active")
