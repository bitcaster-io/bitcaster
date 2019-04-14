# -*- coding: utf-8 -*-
import logging

from django.contrib import admin

from bitcaster.models import Counter, Notification, Occurence

from .site import site

logger = logging.getLogger(__name__)


@admin.register(Counter, site=site)
class CounterAdmin(admin.ModelAdmin):
    list_display = ('target', 'total', 'errors')


@admin.register(Occurence, site=site)
class OccurenceAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'event', 'submissions', 'successes', 'failures')


@admin.register(Notification, site=site)
class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    list_display = ('timestamp', 'application', 'event', 'subscription', 'channel', 'status')
    list_filter = ('status', 'application', 'channel')
