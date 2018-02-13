from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.postgres import fields as pg
from django.contrib.postgres.forms import JSONField, ValidationError
from django.forms import Form
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from admin_extra_urls.extras import ExtraUrlMixin, action
from jsoneditor.forms import JSONEditor

from mercury.exceptions import PluginValidationError
from strategy_field.utils import fqn

from mercury.logging import getLogger
from mercury.models import ApiAuthToken, Application, Channel, Event, User
from mercury.models.message import Message
from mercury.models.subscription import Subscription
from mercury.tasks import emit_event
from mercury.utils.django import (activator_factory,
                                  deactivator_factory, toggler_factory, )

from .forms import (ApplicationForm, DispatcherConfigForm,
                    EventForm, MessageForm, SubscriptionForm, )
from .inlines import ApiTokenInline, ChannelInline, EventInline, MessageInline
from .site import site

logger = getLogger(__name__)
csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


@admin.register(User, site=site)
class UserAdmin(UserAdmin):
    inlines = [ApiTokenInline]


@admin.register(Application, site=site)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'timezone', 'owner')
    inlines = [ChannelInline, EventInline]
    filter_horizontal = ('maintainers',)
    form = ApplicationForm


@admin.register(ApiAuthToken, site=site)
class ApiTokenAdmin(admin.ModelAdmin):
    list_display = ('application', 'user', 'token', 'expires_at')


class EventTriggerForm(Form):
    arguments = JSONField(widget=JSONEditor, required=False)

    def __init__(self, event, *args, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)

    def clean(self):
        expected_arguments = self.event.arguments
        arguments = self.cleaned_data['arguments']
        errors = []
        if arguments:
            for k, v in arguments.items():
                if k not in expected_arguments.keys():
                    errors.append('Invalid argument %s' % k)

        if errors:
            raise ValidationError({'arguments': errors})


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
        ctx = {'opts': opts,
               'app_label': opts.app_label,
               'original': event,
               # 'media': self.media + form.media,
               'user_token': request.user.tokens.all().first(),
               'arguments': event.arguments,
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
            ctx['form'] = form
            ctx['media'] = self.media + form.media
            return render(request, 'admin/event_trigger.html', ctx)
        else:
            form = EventTriggerForm(event, request.POST)
            if form.is_valid():
                try:
                    # success, fail = event.emit(form.cleaned_data['arguments'], False)
                    success, fail = emit_event(event, form.cleaned_data['arguments'])
                    self.message_user(request, f"Success:{success} - Failures:{fail}", messages.INFO)

                except Exception as e:
                    logger.exception(e)
                    self.message_user(request, str(e), messages.ERROR)
                    return render(request, 'admin/event_trigger.html', ctx)
            else:
                ctx['form'] = form
                ctx['media'] = self.media + form.media
                return render(request, 'admin/event_trigger.html', ctx)


@admin.register(Message, site=site)
class MessageAdmin(admin.ModelAdmin):
    form = MessageForm
    list_display = ('name', 'event', 'language')
    list_filter = ('event__application', 'language')
    search_fields = ('name',)
    filter_horizontal = ('channels',)

    def get_fieldsets(self, request, obj=None):
        if obj:
            return (
                (None, {
                    'fields': ('language', 'subject', 'body'),
                }),
                ('Configuration', {
                    'classes': ('collapse',),
                    'fields': ('name', 'event', 'channels')
                }),
            )
        else:
            return [(None, {'fields': self.get_fields(request, obj)})]

    def get_exclude(self, request, obj=None):
        if not obj:
            return ('channels',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('event',)
        return []


@admin.register(Subscription, site=site)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('application',
                    'event', 'subscriber', 'channel', 'active')
    list_editable = ('active',)
    list_filter = ('event__application', 'channel', 'active')
    search_fields = ('subscriber__username', 'subscriber__last_name')
    form = SubscriptionForm
    actions = (toggler_factory('active'),
               activator_factory('active'),
               deactivator_factory('active'))

    def application(self, obj):
        return obj.event.application


@admin.register(Channel, site=site)
class ChannelAdmin(ExtraUrlMixin, admin.ModelAdmin):
    list_display = ('name', 'application', 'handler_name', 'enabled')
    list_filter = ('application',)
    list_editable = ('enabled',)
    form = DispatcherConfigForm

    change_form_template = None

    formfield_overrides = {
        pg.JSONField: {'widget': JSONEditor}
    }
    actions = ['validate_channel',
               'activate',
               deactivator_factory('enabled'),
               ]

    def activate(self, request, queryset):
        for channel in queryset.all():
            try:
                channel.handler.validate_configuration(channel.config, True)
                channel.enabled = True
            except PluginValidationError as e:
                channel.enabled = False
                self.message_user(request, f"{channel.name} invalid configuration {e}",
                                  messages.ERROR)
            channel.save()

    def validate_channel(self, request, queryset):
        for channel in queryset.all():
            try:
                channel.handler.validate_configuration(channel.config, True)
            except PluginValidationError as e:
                channel.enabled = False
                channel.save()
                self.message_user(request, f"{channel.name} invalid configuration {e}",
                                  messages.ERROR)

    def get_exclude(self, request, obj=None):
        if not obj:
            return ['config', 'deprecated', 'enabled']

    @action()
    def test(self, request, pk):
        channel = self.get_object(request, pk)
        try:
            channel.handler.test_connection(raise_exception=True)
            self.message_user(request, 'Success')
        except Exception as e:  # pragma: no-cover
            self.message_user(request, str(e), level=messages.ERROR)

    @action()
    def send_sample_message(self, request, pk):
        channel = self.get_object(request, pk)
        opts = channel._meta
        ctx = {'opts': opts,
               'app_label': opts.app_label,
               'original': channel,
               'change': True,
               'is_popup': False,
               'save_as': False,
               'has_delete_permission': False,
               'has_add_permission': False,
               'has_change_permission': False}
        if request.method == 'GET':
            serializer = channel.handler.subscription_class()
            ctx['serializer'] = serializer
            return render(request, 'admin/mercury/channel/test.html', ctx)
        elif request.method == 'POST':
            serializer = channel.handler.subscription_class(data=request.POST)
            if serializer.is_valid():
                s = Subscription(subscriber=request.user,
                                 event=None,
                                 channel=channel,
                                 active=True,
                                 config=serializer.data)
                channel.handler.test_message(s,
                                             "",
                                             request.POST['message'])
            ctx['serializer'] = serializer
            return render(request, 'admin/mercury/channel/test.html', ctx)

    def handler_name(self, obj):
        return fqn(obj.handler) if obj.handler else ''
