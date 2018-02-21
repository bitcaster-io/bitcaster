# -*- coding: utf-8 -*-
import logging

from admin_extra_urls.extras import ExtraUrlMixin, action
from django.contrib import admin, messages
from django.shortcuts import render
from django.urls import reverse

from mercury.models import Event
from mercury.tasks import emit_event
from mercury.utils.django import (activator_factory,
                                  deactivator_factory, toggler_factory,)

from .forms import EventForm, EventTriggerForm
from .inlines import MessageInline
from .site import site

logger = logging.getLogger(__name__)


@admin.register(Event, site=site)
class EventAdmin(ExtraUrlMixin, admin.ModelAdmin):
    form = EventForm
    list_display = ('name', 'application', 'enabled')
    list_filter = ('application', 'enabled')
    search_fields = ('name', 'application__name')
    inlines = [MessageInline]
    actions = [activator_factory('enabled'),
               deactivator_factory('enabled'),
               toggler_factory('enabled')]

    @action()
    def trigger(self, request, id):
        event = self.get_object(request, id)
        opts = event._meta
        key = request.user.triggers.filter(application=event.application).first()
        if not key:
            key = request.user.triggers.create(application=event.application)
        ctx = {'opts': opts,
               'app_label': opts.app_label,
               'original': event,
               # 'media': self.media + form.media,
               'user_token': key,
               'arguments': event.arguments or {},
               # 'arguments': json.dumps(event.arguments),
               'api_url': request.build_absolute_uri(reverse('api:application-event-trigger',
                                                             args=[event.application.pk, event.pk])),
               'change': True,
               'is_popup': False,
               'save_as': False,
               'has_delete_permission': False,
               'has_add_permission': False,
               'has_change_permission': False}

        if request.method == 'GET':
            form = EventTriggerForm(event,
                                    initial={'arguments': event.arguments})
            # return render(request, 'admin/event_trigger.html', ctx)
        else:
            form = EventTriggerForm(event, request.POST)
            if form.is_valid():
                try:
                    # success, fail = event.emit(form.cleaned_data['arguments'], False)
                    success, fail = emit_event(event, form.cleaned_data['arguments'])
                    self.message_user(request, f"Success:{success} - Failures:{fail}", messages.INFO)
                    # return render(request, 'admin/event_trigger.html', ctx)

                except Exception as e:
                    logger.exception(e)
                    self.message_user(request, str(e), messages.ERROR)
                # return render(request, 'admin/event_trigger.html', ctx)
            # else:
            #     ctx['form'] = form
            #     ctx['media'] = self.media + form.media
        ctx['form'] = form
        ctx['media'] = self.media + form.media
        return render(request, 'admin/event_trigger.html', ctx)
