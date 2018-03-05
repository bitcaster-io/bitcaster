from admin_extra_urls.extras import ExtraUrlMixin, action
from django.contrib import admin, messages
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.postgres import fields as pg
from django.db import router, transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from jsoneditor.forms import JSONEditor
from rest_framework.reverse import reverse
from strategy_field.utils import fqn

from mercury.exceptions import PluginValidationError
from mercury.logging import getLogger
from mercury.models import Channel, Event
from mercury.models.subscription import Subscription
from mercury.utils.django import deactivator_factory

from .forms import ChannelForm
from .site import site

logger = getLogger(__name__)
csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


@admin.register(Channel, site=site)
class ChannelAdmin(ExtraUrlMixin, admin.ModelAdmin):
    list_display = ('name', 'application', 'handler_name', 'enabled')
    list_filter = ('application',)
    list_editable = ('enabled',)
    form = ChannelForm

    change_form_template = None

    formfield_overrides = {
        pg.JSONField: {'widget': JSONEditor}
    }
    actions = ['validate_channel',
               'activate',
               deactivator_factory('enabled'),
               ]

    @action()
    def configure(self, request, pk):
        channel = self.get_object(request, pk)
        opts = channel._meta
        ctx = {'opts': opts,
               'app_label': opts.app_label,
               'original': channel,
               'media': '',
               'title': '',
               'handler_fqn': fqn(channel.handler),
               'change': True,
               'is_popup': False,
               'save_as': False,
               'has_permission': True,
               'has_delete_permission': False,
               'has_add_permission': False,
               'has_change_permission': False}
        if hasattr(channel.handler, 'oauth_request'):
            ctx['oauth_request'] = True

        if request.method == 'GET':
            serializer = channel.handler.options_class(instance=channel.config)
            ctx['serializer'] = serializer
            return render(request, 'admin/mercury/channel/configure.html', ctx)
        elif request.method == 'POST':
            serializer = channel.handler.options_class(data=request.POST)
            ctx['serializer'] = serializer
            try:
                if serializer.is_valid():
                    channel.config = serializer.data
                    channel.save()
                    self.message_user(request, _('Configuration saved'),
                                      messages.SUCCESS)
                    return HttpResponseRedirect(reverse("admin:mercury_channel_change",
                                                args=[channel.pk]))
            except Exception as e:  # pragma: no-cover
                self.message_user(request, str(e), messages.ERROR)
            return render(request, 'admin/mercury/channel/configure.html', ctx)

    def activate(self, request, queryset):
        for channel in queryset.all():
            try:
                channel.handler.validate_configuration(channel.config, True)
                channel.enabled = True
            except PluginValidationError as e:  # pragma: no-cover
                channel.enabled = False
                self.message_user(request, f"{channel.name} invalid configuration {e}",
                                  messages.ERROR)
            channel.save()

    def validate_channel(self, request, queryset):
        for channel in queryset.all():
            try:
                channel.handler.validate_configuration(channel.config, True)
            except PluginValidationError as e:  # pragma: no-cover
                channel.enabled = False
                channel.save()
                self.message_user(request, f"{channel.name} invalid configuration {e}",
                                  messages.ERROR)

    def get_exclude(self, request, obj=None):
        if not obj:
            return ['config', 'deprecated', 'enabled']
        return ['config']

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
            ctx['serializer'] = serializer
            try:
                if serializer.is_valid():
                    s = Subscription(subscriber=request.user,
                                     event=Event(),
                                     channel=channel,
                                     active=True,
                                     config=serializer.data)
                    channel.handler.test_message(s,
                                                 "",
                                                 request.POST['message'])
                    self.message_user(request, _("Message successully sent"), messages.SUCCESS)
                    return HttpResponseRedirect(reverse("admin:mercury_channel_send_sample_message",
                                                args=[channel.pk]))

            except Exception as e:  # pragma: no-cover
                self.message_user(request, str(e), messages.ERROR)
            return render(request, 'admin/mercury/channel/test.html', ctx)

    @action(visible=False)
    def oauth_request(self, request, object_id):
        url = reverse(admin_urlname(self.model._meta, 'change'),
                      args=[object_id],
                      request=request)

        obj = self.get_object(request, object_id)
        return obj.handler.oauth_request(request, url)

    def handler_name(self, obj):
        return fqn(obj.handler) if obj.handler else ''

    def add_view(self, request, form_url='', extra_context=None):
        return self.changeform_view(request, None, form_url, extra_context)

    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     obj = self.get_object(request, object_id)
    #     if hasattr(obj.handler, 'oauth_request'):
    #         extra_context = {'oauth_request': '------'}
    #
    #     return self.changeform_view(request, object_id, form_url, extra_context)

    @csrf_protect_m
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        with transaction.atomic(using=router.db_for_write(self.model)):
            return self._changeform_view(request, object_id, form_url, extra_context)
