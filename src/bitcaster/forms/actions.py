from django import forms
from django.contrib.admin.helpers import ActionForm


class GenericActionForm(ActionForm):
    _selected_action = forms.CharField(label="", widget=forms.MultipleHiddenInput)
