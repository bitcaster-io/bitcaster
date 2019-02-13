# -*- coding: utf-8 -*-
import logging

from admin_extra_urls.extras import ExtraUrlMixin, link
from django.contrib import admin

from bitcaster.models import Registry

from .site import site

logger = logging.getLogger(__name__)


@admin.register(Registry, site=site)
class RegistryAdmin(ExtraUrlMixin, admin.ModelAdmin):
    list_display = ('name', 'enabled', 'version', 'is_core')
    list_filter = ('enabled', 'is_core')
    readonly_fields = ('name', 'enabled', 'version', 'is_core', 'handler', 'description')
    list_editable = ('enabled',)

    @link()
    def inspect(self, request):
        Registry.objects.inspect()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
