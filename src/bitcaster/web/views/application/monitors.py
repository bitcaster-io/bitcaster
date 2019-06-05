from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from django.views.generic.detail import SingleObjectMixin
from formtools.wizard.forms import ManagementForm
from formtools.wizard.views import SessionWizardView
from strategy_field.utils import import_by_name

from bitcaster import messages
from bitcaster.agents.registry import agent_registry
from bitcaster.models import Monitor
from bitcaster.web.forms import MonitorCreate1, MonitorUpdateConfigurationForm
from bitcaster.web.views.base import (BitcasterBaseDeleteView,
                                      BitcasterBaseDetailView,
                                      BitcasterBaseListView,
                                      BitcasterBaseToggleView,
                                      BitcasterBaseUpdateView,)
from bitcaster.web.views.mixins import MessageUserMixin

from .mixins import SelectedApplicationMixin


class MonitorMixin(SelectedApplicationMixin):
    model = Monitor

    def get_queryset(self):
        return self.selected_application.monitors.valid()

    def get_success_url(self):
        return self.selected_application.urls.monitors

    def get_redirect_url(self, *args, **kwargs):
        return self.selected_application.urls.monitors


class ApplicationMonitorList(MonitorMixin, BitcasterBaseListView):
    template_name = 'bitcaster/application/monitors/list.html'


class ApplicationMonitorUsage(MonitorMixin, BitcasterBaseDetailView):
    pass


class ApplicationMonitorUpdate(MonitorMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/application/monitors/form.html'
    form_class = MonitorUpdateConfigurationForm
    # title = _('Edit Monitor')
    permissions = ['manage_monitor']

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'application': self.selected_application})
        return kwargs


class ApplicationMonitorRemove(MonitorMixin, BitcasterBaseDeleteView):
    permissions = ['manage_monitor']


class ApplicationMonitorToggle(MonitorMixin, BitcasterBaseToggleView):
    permissions = ['manage_monitor']

    def get_redirect_url(self, *args, **kwargs):
        return self.get_success_url()


class ApplicationMonitorTest(MonitorMixin, SingleObjectMixin, MessageUserMixin, RedirectView):
    permissions = ['manage_monitor']

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.handler.test()
            self.message_user('Success', messages.SUCCESS)
        except Exception as e:
            self.message_user(str(e), messages.ERROR)
        return super().get(request, *args, **kwargs)


class ApplicationMonitorCreate(MonitorMixin, MessageUserMixin, SessionWizardView):
    permissions = ['manage_monitor']
    title = _('Create Monitor')

    TEMPLATES = {'a': 'bitcaster/application/monitors/create_wizard_1.html',
                 'b': 'bitcaster/application/monitors/create_wizard_2.html',
                 }

    form_list = [('a', MonitorCreate1),
                 ('b', MonitorUpdateConfigurationForm),
                 # todo: add summary screen
                 ]

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
        kwargs = {'application': self.selected_application}
        if step == 'b':
            data = self.storage.get_step_data('a')
            if data:
                handler_fqn = data.get('a-handler')
                handler = import_by_name(handler_fqn)
                kwargs['handler'] = handler
        return kwargs

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current == 'a':
            handler_fqn = self.get_all_cleaned_data().get('handler', None)
            context.update({'registry': agent_registry,
                            'selection': handler_fqn
                            })
        else:
            context.update({'handler': self.storage.extra_data['handler']})
        return context

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        form1, form2 = list(form_list)
        if form1.is_valid():
            try:
                data = self.get_all_cleaned_data()
                data.update({'application': self.selected_application,
                             'config': form2.serializer.data})
                self.object = self.selected_application.monitors.create(**dict(data))
            except IntegrityError as e:
                self.message_user(e, messages.ERROR, extra_tags='keep')

                # this is real ugly. there is a bug somewhere that
                # prevents a simple `self.storage.current_step = 'b'`
                # to work properly. So we totally fake 'steps' entry
                self.storage.current_step = 'b'
                context = self.get_context_data(form=form1, **kwargs)
                context['wizard'] = {
                    'form': form1,
                    'steps': {'prev': 'a', 'current': 'b',
                              'step1': '2', 'count': '2'},
                    'management_form': ManagementForm(prefix=self.prefix,
                                                      initial={
                                                          'current_step': 'b',
                                                      }),
                }
                return self.render_to_response(context)

        self.message_user(_('Monitor created'))
        return HttpResponseRedirect(self.get_success_url())
