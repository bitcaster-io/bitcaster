from admin_extra_urls.extras import link
from django.contrib import admin

from bitcaster.models import ErrorEntry

from ._mixins import TruncateTableMixin
from .site import site


@admin.register(ErrorEntry, site=site)
class ErrorEntryAdmin(TruncateTableMixin, admin.ModelAdmin):
    list_display = ('timestamp', 'application', 'actor', 'target', 'message')
    list_filter = ('application', 'actor_content_type')

    @link()
    def consolidate(self, request):
        ErrorEntry.objects.consolidate()
