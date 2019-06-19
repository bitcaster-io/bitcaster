import logging

from adminfilters.filters import ForeignKeyFieldFilter, RelatedFieldComboFilter
from django.contrib import admin

from bitcaster.models import Subscription
from bitcaster.utils.django import deactivator_factory

from .forms import SubscriptionForm
from .site import site

logger = logging.getLogger(__name__)


@admin.register(Subscription, site=site)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('event', 'subscriber', 'recipient', 'assignment',
                    'channel', 'enabled', 'status')
    list_editable = ('enabled',)
    list_filter = ('event__application',
                   ('channel', RelatedFieldComboFilter),
                   ForeignKeyFieldFilter.factory('subscriber|name|icontains'),
                   'enabled', 'status')
    search_fields = ('subscriber__email', 'subscriber__last_name')
    form = SubscriptionForm
    actions = ('activate',
               deactivator_factory('enabled'))

    def get_exclude(self, request, obj=None):
        if not obj:
            return ['config', 'enabled']

    def application(self, obj):
        return obj.event.application
