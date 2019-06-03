import logging
import uuid

from admin_extra_urls.extras import ExtraUrlMixin, action
from django.contrib import admin, messages
from django.db.models import Count
from django.shortcuts import render

from bitcaster.models import Event
from bitcaster.tasks.event import trigger_event
from bitcaster.utils.django import (activator_factory,
                                    deactivator_factory, toggler_factory,)
# from .forms.event import EventForm, EventTriggerForm
from bitcaster.web.forms.event import EventTriggerForm

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

    @action()
    def trigger(self, request, id):
        event = self.get_object(request, id)
        opts = event._meta
        key = event.application.keys.filter(events=event).first()
        if not key:
            key = event.application.keys.create(name=uuid.uuid4())
            key.events.add(event)
        subscriptions = event.subscriptions.valid().values('channel').annotate(dcount=Count('channel'))
        if not subscriptions:
            self.message_user(request, 'Warning no valid subscriptions for this event',
                              messages.WARNING)
        ctx = {'opts': opts,
               'app_label': opts.app_label,
               'original': event,
               'subscriptions': subscriptions,
               # 'media': self.media + form.media,
               'user_token': key,
               'arguments': event.arguments or {},
               # 'arguments': json.dumps(event.arguments),
               'api_url': event.get_api_url(),
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
                    success, fail = trigger_event.delay(event.pk,
                                               form.cleaned_data['arguments'])
                    self.message_user(request, f'Success:{success} - Failures:{fail}', messages.INFO)
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
