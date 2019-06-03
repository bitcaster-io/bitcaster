import logging

from django.contrib import admin

from bitcaster.models import Counter, Occurence

from .site import site

logger = logging.getLogger(__name__)


@admin.register(Counter, site=site)
class CounterAdmin(admin.ModelAdmin):
    list_display = ('target', 'total', 'errors')


@admin.register(Occurence, site=site)
class OccurenceAdmin(admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    list_display = ('timestamp', 'event', 'expire', 'status', 'id',
                    'submissions', 'successes', 'failures')
    list_filter = ('expire', 'status')
