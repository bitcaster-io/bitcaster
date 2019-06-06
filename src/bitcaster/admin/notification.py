from admin_extra_urls.extras import ExtraUrlMixin, link
from django.contrib import admin

from bitcaster.models import Notification

from .site import site


@admin.register(Notification, site=site)
class NotificationAdmin(ExtraUrlMixin, admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    list_display = ('timestamp', 'occurence', 'event', 'channel', 'address', 'status',
                    'need_confirmation', 'send', 'next_sent', 'a')
    list_filter = ('status', 'application', 'channel')
    exclude = ('attachments',)

    @link()
    def consolidate(self, request):
        Notification.objects.consolidate()

    def a(self, obj):
        return obj.attachments[0].name

    def send(self, obj):
        return '%d/%d' % (obj.reminders or 0, obj.max_reminders or 0)
