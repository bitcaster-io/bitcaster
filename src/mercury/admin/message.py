# -*- coding: utf-8 -*-
import logging
from django.contrib import admin

from mercury.models import Message

from .forms import MessageForm
from .site import site

logger = logging.getLogger(__name__)


@admin.register(Message, site=site)
class MessageAdmin(admin.ModelAdmin):
    form = MessageForm
    list_display = ('name', 'event', 'language')
    list_filter = ('event__application', 'language')
    search_fields = ('name',)
    filter_horizontal = ('channels',)

    def get_fieldsets(self, request, obj=None):
        if obj:
            return (
                (None, {
                    'fields': ('language', 'subject', 'body'),
                }),
                ('Configuration', {
                    'classes': ('collapse',),
                    'fields': ('name', 'event', 'channels')
                }),
            )
        else:
            return [(None, {'fields': self.get_fields(request, obj)})]

    def get_exclude(self, request, obj=None):
        if not obj:
            return ('channels',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('event',)
        return []
