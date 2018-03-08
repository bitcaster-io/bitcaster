# -*- coding: utf-8 -*-
import logging

from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from django.views.generic import ListView
from formtools.wizard.views import SessionWizardView
from strategy_field.utils import import_by_name

from mercury.dispatchers import dispatcher_registry
from mercury.models import Channel
from mercury.web.views.base import (MercuryBaseCreateView, MessageUserMixin,
                                    SelectedApplicationMixin,)

logger = logging.getLogger(__name__)


class ChannelMixin:
    model = Channel


class ChannelCreateView(ChannelMixin, MercuryBaseCreateView):
    pass


class ChannelCreate1(forms.ModelForm):
    handler = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = Channel
        fields = ('handler',)


class ChannelCreate2(forms.ModelForm):
    class Meta:
        model = Channel
        fields = ('name', 'description')


class ChannelCreate3(forms.Form):
    config = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.serializer_class = kwargs.pop("serializer")
        super().__init__(*args, **kwargs)

    class Meta:
        fields = ()

    @cached_property
    def serializer(self):
        if self.data:
            ser = self.serializer_class(data=self.data)
            ser.is_valid()
            return ser
        return self.serializer_class()

    def is_valid(self):
        valid = super().is_valid()
        if self.serializer_class:
            valid = valid and self.serializer.is_valid()
        return valid


class ChannelCreate4(forms.Form):
    pass


class SystemChannelCreateWizard(MessageUserMixin, SessionWizardView):
    form_list = [("a", ChannelCreate1),
                 ("b", ChannelCreate2),
                 ("c", ChannelCreate3),
                 # todo: add summary screen
                 # ("d", ChannelCreate4)
                 ]
    TEMPLATES = {"a": "bitcaster/channel_wizard1.html",
                 "b": "bitcaster/channel_wizard2.html",
                 "c": "bitcaster/channel_wizard3.html",
                 # "d": "bitcaster/channel_wizard4.html",
                 }

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
        elif self.steps.current == 'c':
            self.storage.extra_data['config'] = form.serializer.data
        return ret

    # def get_form_instance(self, step):
    #     return super().get_form_instance(step)

    def get_form_kwargs(self, step=None):
        kwargs = {}
        if step == 'c':
            kwargs = {'serializer': None}
            data = self.storage.get_step_data('a')
            if data:
                handler_fqn = data.get('a-handler')
                handler = import_by_name(handler_fqn)
                kwargs = {'serializer': handler.options_class}

        return kwargs

    def get_context_data(self, form, **kwargs):
        context = super(SystemChannelCreateWizard, self).get_context_data(form=form, **kwargs)
        handler_fqn = self.get_all_cleaned_data().get('handler', None)
        if self.steps.current == 'a':
            context.update({'registry': dispatcher_registry,
                            'selection': handler_fqn
                            })

        return context

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        data = self.get_all_cleaned_data()
        data['config'] = self.storage.extra_data['config']
        data['handler'] = self.storage.extra_data['handler']
        Channel.objects.create(system=True,
                               **data)
        self.message_user(_('Channel created'))
        return HttpResponseRedirect(reverse('settings-channels'))


class ChannelList(SelectedApplicationMixin, ListView):

    def get_queryset(self):
        return self.selected_application.channels.all()
