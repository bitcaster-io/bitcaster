from django.contrib import admin, messages
from django.contrib.postgres import fields as pg
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from admin_extra_urls.extras import ExtraUrlMixin, action
from jsoneditor.forms import JSONEditor
from strategy_field.utils import fqn

from mercury.exceptions import PluginValidationError
from mercury.logging import getLogger
from mercury.models import Channel
from mercury.models.subscription import Subscription
from mercury.utils.django import deactivator_factory

from .forms import DispatcherConfigForm
from .site import site

logger = getLogger(__name__)
csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


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
