from django.contrib import admin

from bitcaster.models import ErrorEntry

from .site import site


@admin.register(ErrorEntry, site=site)
class ErrorEntryAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'actor', 'application', 'actor_label', 'message')
    list_filter = ('application', 'actor_content_type')
