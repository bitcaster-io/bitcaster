from django import forms

from bitcaster.models import Assignment


class AssignmentForm(forms.ModelForm["Assignment"]):
    class Meta:
        model = Assignment
        fields = ("address", "channel", "validated", "active", "data")
