from admin_extra_urls.extras import link
from django.contrib import admin

from bitcaster.models import Notification

from ._mixins import TruncateTableMixin
from .site import site


@admin.register(Notification, site=site)
class NotificationAdmin(TruncateTableMixin, admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    list_display = ('timestamp', 'occurence_id', 'event', 'channel', 'address', 'status',
                    'need_confirmation', 'send', 'next_sent', 'a')
    list_filter = ('status', 'application', 'channel')
    exclude = ('attachments',)

    @link()
    def consolidate(self, request):
        Notification.objects.consolidate()

    def a(self, obj):
        if obj.attachments:
            return obj.attachments[0].name

    def send(self, obj):
        return '%d/%d' % (obj.reminders or 0, obj.max_reminders or 0)
