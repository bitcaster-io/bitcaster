from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, RedirectView
from formtools.wizard.forms import ManagementForm
from formtools.wizard.views import SessionWizardView
from strategy_field.utils import import_by_name

from bitcaster import messages
from bitcaster.agents.registry import agent_registry
from bitcaster.models import Monitor
from bitcaster.web.forms import MonitorCreate1, MonitorUpdateConfigurationForm
from bitcaster.web.views.base import (BitcasterBaseDeleteView,
                                      BitcasterBaseDetailView,
                                      BitcasterBaseUpdateView,)
from bitcaster.web.views.mixins import MessageUserMixin

from .mixins import ApplicationListMixin, SelectedApplicationMixin


class ApplicationMonitorList(SelectedApplicationMixin, ApplicationListMixin, ListView):
    template_name = 'bitcaster/application/monitors/list.html'

    def get_queryset(self):
        return self.selected_application.monitors.valid()

    def get_context_data(self, **kwargs):
        kwargs['channel_context'] = self.selected_application
        kwargs['title'] = _('Application Monitors')
        return super().get_context_data(**kwargs)


class ApplicationMonitorUsage(SelectedApplicationMixin, BitcasterBaseDetailView):
    pass


class ApplicationMonitorUpdate(SelectedApplicationMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/application/monitors/configure.html'
    model = Monitor
    form_class = MonitorUpdateConfigurationForm

    def get_success_url(self):
        return self.object.application.urls.monitors

    def get_queryset(self):
        return self.selected_application.monitors.all()


class ApplicationMonitorRemove(SelectedApplicationMixin, BitcasterBaseDeleteView):

    def get_success_url(self):
        return self.object.application.urls.monitors

    def get_queryset(self):
        return self.selected_application.monitors.all()


class ApplicationMonitorToggle(SelectedApplicationMixin, MessageUserMixin, RedirectView):
    def get_queryset(self):
        return self.selected_application.monitors.all()

    def get_redirect_url(self, *args, **kwargs):
        return self.selected_application.urls.monitors

    def get(self, request, *args, **kwargs):
        obj = self.get_queryset().get(id=kwargs['pk'])
        obj.enabled = not obj.enabled
        obj.save()
        op = 'enabled' if obj.enabled else 'disabled'
        self.message_user(f'Channel {op}')
        return super().get(request, *args, **kwargs)


class ApplicationMonitorTest(SelectedApplicationMixin, MessageUserMixin, RedirectView):
    def get_queryset(self):
        return self.selected_application.monitors.all()

    def get_redirect_url(self, *args, **kwargs):
        return self.selected_application.urls.monitors

    def get(self, request, *args, **kwargs):
        self.object = self.get_queryset().get(id=kwargs['pk'])
        try:
            self.object.handler.test()
        except Exception as e:
            self.message_user(str(e), messages.ERROR)
        return super().get(request, *args, **kwargs)


class ApplicationMonitorCreate(SelectedApplicationMixin, MessageUserMixin, SessionWizardView):
    TEMPLATES = {'a': 'bitcaster/application/monitors/create_wizard_1.html',
                 'b': 'bitcaster/application/monitors/create_wizard_2.html',
                 }

    def get_success_url(self):
        return self.object.application.urls.monitors

    def get_extra_instance_kwargs(self):
        return {'application': self.selected_application}

    form_list = [('a', MonitorCreate1),
                 ('b', MonitorUpdateConfigurationForm),
                 # todo: add summary screen
                 ]

    # success_url = reverse_lazy('settings-channels')

    def get_form_initial(self, step):
        handler = self.storage.extra_data.get('handler', None)
        if step == 'b' and handler:
            return {'name': '%sMonitor' % handler.name}
        return super().get_form_initial(step)

    def process_step(self, form):
        ret = super().process_step(form)
        if self.steps.current == 'a':
            handler_fqn = form.data.get('a-handler')
            self.storage.extra_data['handler'] = import_by_name(handler_fqn)
        return ret

    def get_form_kwargs(self, step=None):
        kwargs = {}
        if step == 'b':
            kwargs = {'serializer': None}
            data = self.storage.get_step_data('a')
            if data:
                handler_fqn = data.get('a-handler')
                handler = import_by_name(handler_fqn)
                kwargs = {'serializer': handler.options_class}

        return kwargs

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        handler_fqn = self.get_all_cleaned_data().get('handler', None)
        if self.steps.current == 'a':
            context.update({'registry': agent_registry,
                            'selection': handler_fqn
                            })
        else:
            context.update({'handler': self.storage.extra_data['handler']})
        return context

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        data = self.get_all_cleaned_data()
        data.update(self.get_extra_instance_kwargs())
        try:
            self.object = Monitor.objects.create(**dict(data))
        except IntegrityError:
            h = self.storage.extra_data['handler']

            data = self.get_all_cleaned_data()

            form = MonitorUpdateConfigurationForm(data=data,
                                                  serializer=h.options_class)

            self.message_user(_('Error creating channel. '
                                'Channel with this name already exists.'),
                              messages.ERROR)

            # this is real ugly. there is a bug somewhere that
            # prevents a simple `self.storage.current_step = 'b'`
            # to work properly. So we totally fake 'steps' entry
            self.storage.current_step = 'b'
            context = self.get_context_data(form=form, **kwargs)
            context['wizard'] = {
                'form': form,
                'steps': {'prev': 'a', 'current': 'b',
                          'step1': '2', 'count': '2'},
                'management_form': ManagementForm(prefix=self.prefix, initial={
                    'current_step': 'b',
                }),
            }
            return self.render_to_response(context)

        self.message_user(_('Channel created'))
        return HttpResponseRedirect(self.get_success_url())
