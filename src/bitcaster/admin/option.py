import logging

from django.contrib import admin

from bitcaster.models import Option, OrganizationOption

from .site import site

logger = logging.getLogger(__name__)


@admin.register(Option, site=site)
class OptionAdmin(admin.ModelAdmin):
    search_fields = ('key',)
    list_display = ('key', 'value', 'last_updated')
    list_filter = ('last_updated',)


@admin.register(OrganizationOption, site=site)
class OrganizationOptionAdmin(admin.ModelAdmin):
    search_fields = ('key',)
    list_display = ('key', 'value', 'last_updated')
    list_filter = ('last_updated',)
