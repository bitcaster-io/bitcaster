from django import forms


class GenericActionForm(forms.Form):
    _selected_action = forms.CharField(label="", widget=forms.MultipleHiddenInput)
    select_across = forms.BooleanField(
        label="",
        required=False,
        initial=0,
        widget=forms.HiddenInput({"class": "select-across"}),
    )
    action = forms.CharField(label="", required=True, initial="", widget=forms.HiddenInput())
