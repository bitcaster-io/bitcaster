# -*- coding: utf-8 -*-
import logging

from adminfilters.filters import ForeignKeyFieldFilter, RelatedFieldComboFilter
from django.contrib import admin, messages

from bitcaster.exceptions import PluginValidationError
from bitcaster.models import Subscription
from bitcaster.utils.django import deactivator_factory

from .forms import SubscriptionForm
from .site import site

logger = logging.getLogger(__name__)


@admin.register(Subscription, site=site)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('application',
                    'event', 'subscriber', 'trigger_by', 'channel', 'enabled')
    list_editable = ('enabled',)
    list_filter = ('event__application',
                   ('channel', RelatedFieldComboFilter),
                   ForeignKeyFieldFilter.factory('subscriber|name|icontains'),
                   'enabled')
    search_fields = ('subscriber__username', 'subscriber__last_name')
    form = SubscriptionForm
    actions = ('activate',
               'validate_subscription',
               deactivator_factory('enabled'))

    def get_exclude(self, request, obj=None):
        if not obj:
            return ['config', 'enabled']
        # elif hasattr(obj.handler, 'oauth_request'):
        #     return ['config']

    def application(self, obj):
        return obj.event.application

    def activate(self, request, queryset):
        for subscription in queryset.all():
            try:
                subscription.channel.validate_subscription(subscription)
                subscription.enabled = True
            except PluginValidationError as e:
                subscription.enabled = False
                self.message_user(request, f'{subscription}: Invalid configuration {e}',
                                  messages.ERROR)
            subscription.save()

    def validate_subscription(self, request, queryset):
        for subscription in queryset.all():
            try:
                subscription.channel.validate_subscription(subscription)
            except PluginValidationError as e:
                subscription.enabled = False
                subscription.save()
                self.message_user(request, f'{subscription.id} invalid configuration {e}',
                                  messages.ERROR)

    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     obj = self.get_object(request, object_id)
    #     # extra_context = {'show_save_and_continue': False}
    #     return self.changeform_view(request, object_id, form_url, extra_context)
