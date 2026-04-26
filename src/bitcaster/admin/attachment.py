from bitcaster.models import Attachment

from .base import BaseAdmin


class AttachmentAdmin(BaseAdmin[Attachment]):
    list_display = ("pk", "application", "filename", "correlation_id")
