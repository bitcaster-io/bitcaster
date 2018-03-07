# -*- coding: utf-8 -*-
import logging

from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView
from formtools.wizard.views import SessionWizardView
from strategy_field.utils import import_by_name

from mercury.dispatchers import dispatcher_registry
from mercury.models import Channel
from mercury.web.views.base import (MercuryBaseCreateView,
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
        fields = ('name',)


class ChannelCreate3(forms.ModelForm):
    config = forms.Textarea()

    class Meta:
        model = Channel
        fields = ('config',)


class ChannelCreate4(forms.Form):
    class Meta:
        pass


class SystemChannelCreateWizard(SessionWizardView):
    form_list = [("a", ChannelCreate1),
                 ("b", ChannelCreate2),
                 ("c", ChannelCreate3)]
    TEMPLATES = {"a": "bitcaster/channel_wizard1.html",
                 "b": "bitcaster/channel_wizard2.html",
                 "c": "bitcaster/channel_wizard3.html",
                 }

    def get_context_data(self, form, **kwargs):
        context = super(SystemChannelCreateWizard, self).get_context_data(form=form, **kwargs)
        handler_fqn = self.get_all_cleaned_data().get('handler', None)
        if self.steps.current == 'a':
            context.update({'registry': dispatcher_registry,
                            'selection': handler_fqn
                            })
        elif self.steps.current == 'b':
            pass
        elif self.steps.current == 'c':
            handler = import_by_name(handler_fqn)
            data = self.storage.get_step_data('c') or {}
            if data:
                serializer = handler.options_class(data=data)
                serializer.is_valid()
            else:
                serializer = handler.options_class()
            context.update({'serializer': serializer})
        return context

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        data = self.get_all_cleaned_data()
        config = self.storage.get_step_data('c')
        handler = import_by_name(data['handler'])
        serializer = handler.options_class(data=config)
        if serializer.is_valid():
            data['config'] = serializer.data
            Channel.objects.create(system=True,
                                   **data)
        else:
            return self.render_goto_step('c')
        return HttpResponseRedirect(reverse('settings-channels'))


class ChannelList(SelectedApplicationMixin, ListView):

    def get_queryset(self):
        return self.selected_application.channels.all()
