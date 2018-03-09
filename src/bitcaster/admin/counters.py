# -*- coding: utf-8 -*-
import logging

from django.contrib import admin

from bitcaster.models import Counter, Occurence
from bitcaster.models.counters import LogEntry

from .site import site

logger = logging.getLogger(__name__)


@admin.register(Counter, site=site)
class CounterAdmin(admin.ModelAdmin):
    list_display = ('target', 'total', 'errors')


@admin.register(Occurence, site=site)
class OccurenceAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'event', 'submissions', 'successes', 'failures')


@admin.register(LogEntry, site=site)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'application', 'event', 'subscription', 'channel')
