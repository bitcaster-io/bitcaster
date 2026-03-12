from constance.admin import ConstanceAdmin
from constance.base import Config
from constance.forms import ConstanceForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from bitcaster.admin.base import BitcasterModelAdmin
from bitcaster.auth.constants import DEFAULT_OCCURRENCE_DEFAULT_RETENTION, DEFAULT_OCCURRENCE_MAX_RETENTION
from bitcaster.forms.unfold import UnfoldForm


class CustomConstanceForm(UnfoldForm, ConstanceForm):
    def clean(self):
        cleaned_data = super().clean()
        default_val = cleaned_data.get("OCCURRENCE_DEFAULT_RETENTION", DEFAULT_OCCURRENCE_DEFAULT_RETENTION)
        max_val = cleaned_data.get("OCCURRENCE_MAX_RETENTION", DEFAULT_OCCURRENCE_MAX_RETENTION)

        if default_val > max_val:
            raise ValidationError(_("Default retention cannot be greater than maximum retention."))


class CustomConstanceAdmin(ConstanceAdmin, BitcasterModelAdmin[Config]):
    change_list_form = CustomConstanceForm
