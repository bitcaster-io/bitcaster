from admin_extra_urls.extras import ExtraUrlMixin, action
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework.fields import empty
from rest_framework.reverse import reverse
from strategy_field.utils import fqn

from bitcaster.exceptions import PluginValidationError
from bitcaster.logging import getLogger
from bitcaster.models import Monitor
from bitcaster.templatetags.bitcaster import render_serializer
from bitcaster.utils.django import deactivator_factory

from .site import site

logger = getLogger(__name__)
csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


@admin.register(Monitor, site=site)
class MonitorAdmin(ExtraUrlMixin, admin.ModelAdmin):
    list_display = ('name', 'organization', 'application',
                    'handler_name', 'enabled',)
    list_filter = ('application', 'enabled',)
    list_editable = ('enabled',)

    change_form_template = None

    actions = ['validate_monitor',
               'activate',
               deactivator_factory('enabled'),
               ]

    @action()
    def configure(self, request, pk):
        monitor = self.get_object(request, pk)
        opts = monitor._meta
        ctx = {'opts': opts,
               'app_label': opts.app_label,
               'original': monitor,
               'media': '',
               'title': '',
               'handler_fqn': fqn(monitor.handler),
               'change': True,
               'is_popup': False,
               'save_as': False,
               'has_permission': True,
               'has_delete_permission': False,
               'has_add_permission': False,
               'has_change_permission': False}
        if hasattr(monitor.handler, 'oauth_request'):
            ctx['oauth_request'] = True

        if request.method == 'GET':
            # form = MonitorUpdateConfigurationForm(instance=monitor,
            #                                       serializer=monitor.handler.options_class)
            # serializer = monitor.handler.options_class(instance=monitor.config)
            serializer = monitor.handler.get_options_form(data=monitor.config)
            serializer.is_valid()
            try:
                render_serializer(serializer, 'rest_framework/inline2')
            except Exception as e:
                self.message_user(request,
                                  f'Error {e}'
                                  'Invalid configuration found. All data has been cleared',
                                  messages.ERROR)
            # serializer = monitor.handler.options_class()
            ctx['serializer'] = serializer
            return render(request, 'admin/bitcaster/monitor/configure.html', ctx)
        else:  # if request.method == 'POST':
            ser = monitor.handler.options_class
            data = {k: v for k, v in request.POST.dict().items()
                    if k in ser().get_fields().keys()}

            serializer = monitor.handler.get_options_form(data=data or empty)
            # serializer = monitor.handler.options_class(data=request.POST)
            # serializer.fields['event'].choices = monitor.application.events.values_list('id', 'name')

            ctx['serializer'] = serializer
            try:
                if serializer.is_valid():
                    monitor.config = serializer.data
                    monitor.save()
                    self.message_user(request, _('Configuration saved'), messages.SUCCESS)
                    return HttpResponseRedirect(reverse('admin:bitcaster_monitor_change',
                                                        args=[monitor.pk]))
            except Exception as e:  # pragma: no-cover
                self.message_user(request, str(e), messages.ERROR)
            return render(request, 'admin/bitcaster/monitor/configure.html', ctx)

    def activate(self, request, queryset):
        for monitor in queryset.all():
            try:
                monitor.handler.validate_configuration(monitor.config, True)
                monitor.enabled = True
            except PluginValidationError as e:  # pragma: no-cover
                monitor.enabled = False
                self.message_user(request, f'{monitor.name} invalid configuration {e}',
                                  messages.ERROR)
            monitor.save()

    def validate_monitor(self, request, queryset):
        for monitor in queryset.all():
            try:
                monitor.handler.validate_configuration(monitor.config, True)
            except PluginValidationError as e:  # pragma: no-cover
                monitor.enabled = False
                monitor.save()
                self.message_user(request, f'{monitor.name} invalid configuration {e}',
                                  messages.ERROR)

    def get_exclude(self, request, obj=None):
        if not obj:
            return ['config', 'deprecated', 'enabled']
        return ['config']

    @action()
    def test(self, request, pk):
        monitor = self.get_object(request, pk)
        try:
            monitor.handler.test_connection(raise_exception=True)
            self.message_user(request, 'Success')
        except Exception as e:  # pragma: no-cover
            self.message_user(request, str(monitor.config), level=messages.ERROR)
            self.message_user(request, str(e), level=messages.ERROR)

    @action()
    def poll(self, request, pk):
        monitor = self.get_object(request, pk)
        try:
            monitor.handler.poll()
            self.message_user(request, 'Success')
        except Exception as e:  # pragma: no-cover
            self.message_user(request, str(e), level=messages.ERROR)
