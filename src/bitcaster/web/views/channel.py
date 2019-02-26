# -*- coding: utf-8 -*-
import logging

from django import forms
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from formtools.wizard.forms import ManagementForm
from formtools.wizard.views import SessionWizardView
from strategy_field.utils import import_by_name

from bitcaster.dispatchers import dispatcher_registry
from bitcaster.exceptions import PluginSendError
from bitcaster.models import AddressAssignment, Channel
from bitcaster.templatetags.markdown import markdown
from bitcaster.web.forms.channel import ChannelUpdateConfigurationForm
from bitcaster.web.views.base import (BitcasterBaseCreateView,
                                      BitcasterBaseDeleteView,
                                      BitcasterBaseUpdateView,
                                      BitcasterTemplateView, MessageUserMixin,
                                      SelectedOrganizationMixin,)

logger = logging.getLogger(__name__)


class ChannelCreate1(forms.ModelForm):
    handler = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = Channel
        fields = ('handler',)


class ChannelCreateWizard(MessageUserMixin, SessionWizardView):
    form_list = [('a', ChannelCreate1),
                 ('b', ChannelUpdateConfigurationForm),
                 # todo: add summary screen
                 ]
    TEMPLATES = {'a': 'bitcaster/settings/channel_wizard1.html',
                 'b': 'bitcaster/settings/channel_wizard2.html',
                 }

    # success_url = reverse_lazy('settings-channels')

    def get_form_initial(self, step):
        handler = self.storage.extra_data.get('handler', None)
        if step == 'b' and handler:
            return {'name': '%sChannel' % handler.name}
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
            context.update({'registry': dispatcher_registry,
                            'selection': handler_fqn
                            })
        else:
            context.update({'handler': self.storage.extra_data['handler']})
        return context

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def get_extra_instance_kwargs(self):
        return {}

    def get_success_url(self):
        return self.success_url

    def done(self, form_list, **kwargs):
        data = self.get_all_cleaned_data()
        data.update(self.get_extra_instance_kwargs())
        try:
            Channel.objects.create(**dict(data))
        except IntegrityError as e:
            logger.exception(e)
            h = self.storage.extra_data['handler']

            data = self.get_all_cleaned_data()

            form = ChannelUpdateConfigurationForm(data=data,
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


class ChannelCreateView(BitcasterBaseCreateView):
    model = Channel

    def get_queryset(self):
        return self.selected_organization.channels.all()


class ChannelListView(BitcasterTemplateView):
    pass
    # def get_queryset(self):
    #     raise NotImplementedError
    #
    # def get_context_data(self, **kwargs):
    #     kwargs['channel_context'] = 1111
    #     kwargs['channels'] = self.get_queryset()
    #     return super().get_context_data(**kwargs)


class ChannelUpdateView(BitcasterBaseUpdateView):
    form_class = ChannelUpdateConfigurationForm

    def get_queryset(self):
        return self.selected_organization.channels


class ChannelDeleteView(BitcasterBaseDeleteView):
    def get_queryset(self):
        raise NotImplementedError


class ChannelDeprecateView(SelectedOrganizationMixin, MessageUserMixin, RedirectView):
    # url = reverse_lazy("settings-channels")

    def get_queryset(self):
        raise NotImplementedError

    def get(self, request, *args, **kwargs):
        obj = self.get_queryset().get(id=kwargs['pk'])
        obj.deprecated = not obj.deprecated
        obj.save()
        op = 'hidden' if obj.deprecated else 'visible'
        self.message_user(f'Channel {op}')
        return super().get(request, *args, **kwargs)


class ChannelToggleView(SelectedOrganizationMixin, MessageUserMixin, RedirectView):

    def get_queryset(self):
        raise NotImplementedError

    def get_redirect_url(self, *args, **kwargs):
        raise NotImplementedError

    def get(self, request, *args, **kwargs):
        obj = self.get_queryset().get(id=kwargs['pk'])
        obj.enabled = not obj.enabled
        obj.save()
        op = 'enabled' if obj.enabled else 'disabled'
        self.message_user(f'Channel {op}')
        return super().get(request, *args, **kwargs)


class ChannelTestView(SelectedOrganizationMixin, MessageUserMixin, RedirectView):

    def get_queryset(self):
        raise NotImplementedError

    def get_redirect_url(self, *args, **kwargs):
        raise NotImplementedError

    def get(self, request, *args, **kwargs):
        self.object = self.get_queryset().get(id=kwargs['pk'])
        try:
            dispatcher = self.object.handler
            address = request.user.assignments.get_address(dispatcher)
            dispatcher.emit(address, '-', 'test channel message')

            msg = _("""Message sent to {}""").format(address)
            self.message_user(markdown(msg), messages.SUCCESS)

        except AddressAssignment.DoesNotExist:
            url = reverse('user-address-assignment')
            msg = _("""You do not have a valid address for this channel.
Goto [addresses]({0}) to set your choice for **{1}**""").format(url, self.object.name)
            self.message_user(markdown(msg), messages.ERROR, extra_tags='keep')
        except PluginSendError as e:
            self.message_user(_("Unable to send message to '{}': {}").format(address, e), messages.ERROR)
        return super().get(request, *args, **kwargs)
