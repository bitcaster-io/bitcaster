# -*- coding: utf-8 -*-
import logging
from django.contrib import admin, messages

from mercury.exceptions import PluginValidationError
from mercury.models import Subscription
from mercury.utils.django import deactivator_factory

from .forms import SubscriptionForm
from .site import site

logger = logging.getLogger(__name__)


@admin.register(Subscription, site=site)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('application',
                    'event', 'subscriber', 'channel', 'active')
    list_editable = ('active',)
    list_filter = ('event__application', 'channel', 'active')
    search_fields = ('subscriber__username', 'subscriber__last_name')
    form = SubscriptionForm
    actions = ('activate',
               'validate_subscription',
               deactivator_factory('active'))

    def application(self, obj):
        return obj.event.application

    def activate(self, request, queryset):
        for subscription in queryset.all():
            try:
                subscription.channel.validate_subscription(subscription)
                subscription.active = True
            except PluginValidationError as e:
                subscription.active = False
                self.message_user(request, f"{subscription}: Invalid configuration {e}",
                                  messages.ERROR)
            subscription.save()

    def validate_subscription(self, request, queryset):
        for subscription in queryset.all():
            try:
                subscription.channel.validate_subscription(subscription, True)
            except PluginValidationError as e:
                subscription.enabled = False
                subscription.save()
                self.message_user(request, f"{subscription.name} invalid configuration {e}",
                                  messages.ERROR)
