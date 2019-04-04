import logging

from django import forms

logger = logging.getLogger(__name__)


class AutompleteMixin:
    autocomplete = ''

    def __init__(self):
        super().__init__()
        self.attrs['autocomplete'] = self.autocomplete


class EmailInput(AutompleteMixin, forms.EmailInput):
    autocomplete = 'email'


class EmailField(forms.EmailField):
    widget = EmailInput
