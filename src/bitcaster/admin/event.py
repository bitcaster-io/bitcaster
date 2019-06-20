import logging

from admin_extra_urls.extras import ExtraUrlMixin
from django.contrib import admin

from bitcaster.models import Event
from bitcaster.utils.django import (activator_factory,
                                    deactivator_factory, toggler_factory,)

from .inlines import MessageInline
from .site import site

logger = logging.getLogger(__name__)


@admin.register(Event, site=site)
class EventAdmin(ExtraUrlMixin, admin.ModelAdmin):
    # form = EventForm
    list_display = ('name', 'application', 'enabled')
    list_filter = ('application', 'enabled')
    search_fields = ('name', 'application__name')
    inlines = [MessageInline]
    actions = [activator_factory('enabled'),
               deactivator_factory('enabled'),
               toggler_factory('enabled')]
