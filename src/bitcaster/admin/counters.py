import logging

from admin_extra_urls.extras import ExtraUrlMixin, link
from django.contrib import admin

from bitcaster.models import Counter, Occurence

from .site import site

logger = logging.getLogger(__name__)


@admin.register(Counter, site=site)
class CounterAdmin(admin.ModelAdmin):
    list_display = ('target', 'total', 'errors')


@admin.register(Occurence, site=site)
class OccurenceAdmin(ExtraUrlMixin, admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    list_display = ('timestamp', 'event', 'expire', 'status', 'id',
                    'processing')
    list_filter = ('expire', 'status')

    @link()
    def consolidate(self, request):
        Occurence.objects.consolidate()
