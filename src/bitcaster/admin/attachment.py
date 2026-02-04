from adminfilters.autocomplete import AutoCompleteFilter

from bitcaster.admin.base import BaseAdmin, BitcasterModelAdmin
from bitcaster.forms.attachment import AttachmentForm
from bitcaster.models import Attachment


class AttachmentAdmin(BaseAdmin, BitcasterModelAdmin[Attachment]):
    search_fields = ("filename", "correlation_id")
    list_display = ("filename", "correlation_id", "size", "mime_type")
    list_filter = (("mime_type", AutoCompleteFilter),)
    form = AttachmentForm
