from django.contrib import admin

from bitcaster.models.audit import AuditLogEntry

from ._mixins import TruncateTableMixin
from .site import site


@admin.register(AuditLogEntry, site=site)
class AuditLogEntryAdmin(TruncateTableMixin, admin.ModelAdmin):
    list_display = ('timestamp', 'organization', 'actor', 'target_object',
                    'target_label', 'event', 'ip_address', 'get_message')

    date_hierarchy = 'timestamp'
