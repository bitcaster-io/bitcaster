from django.contrib import admin

from bitcaster.models import ErrorEntry

from .site import site


@admin.register(ErrorEntry, site=site)
class CounterAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'event', 'application', 'target_label')
    list_filter = ('application', 'event')
