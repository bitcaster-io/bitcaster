# -*- coding: utf-8 -*-
import logging

from django.contrib import admin

from bitcaster.models import AuditLogEntry

from .site import site

logger = logging.getLogger(__name__)


@admin.register(AuditLogEntry, site=site)
class AuditLogEntryAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'organization', 'application', 'actor')
    list_filter = ('organization', 'application')
