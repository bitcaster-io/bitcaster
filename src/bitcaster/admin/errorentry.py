from django.contrib import admin

from bitcaster.models import ErrorEntry

from .site import site


@admin.register(ErrorEntry, site=site)
class ErrorEntryAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'target', 'application', 'target_label', 'message')
    list_filter = ('application', 'content_type')
