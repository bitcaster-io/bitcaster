import logging

from django.contrib import admin

from bitcaster.models import Message

from .site import site

logger = logging.getLogger(__name__)


@admin.register(Message, site=site)
class MessageAdmin(admin.ModelAdmin):
    # form = MessageForm
    list_display = ('event', 'channel', 'language')
    list_filter = ('event__application', 'language')
    search_fields = ('name',)

    # def get_fieldsets(self, request, obj=None):
    #     if obj:
    #         return (
    #             (None, {
    #                 'fields': ('language', 'subject', 'body'),
    #             }),
    #             ('Configuration', {
    #                 'classes': ('collapse',),
    #                 'fields': ('name', 'event', 'channel')
    #             }),
    #         )
    #     else:
    #         return [(None, {'fields': self.get_fields(request, obj)})]

    # def get_exclude(self, request, obj=None):
    #     if not obj:
    #         return ('channel',)

    # def get_readonly_fields(self, request, obj=None):
    #     if obj:
    #         return ('event',)
    #     return []
