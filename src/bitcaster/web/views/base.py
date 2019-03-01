# -*- coding: utf-8 -*-
import logging

from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  RedirectView, TemplateView, UpdateView,)
from django.views.generic.detail import SingleObjectMixin
from strategy_field.utils import import_by_name

from bitcaster.templatetags.bitcaster import verbose_name

from .mixins import BitcasterBaseViewMixin, MessageUserMixin

logger = logging.getLogger(__name__)


class BitcasterTemplateView(MessageUserMixin, TemplateView):
    pass


class BitcasterSingleObjectMixin:
    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        vars = dict(kwargs)
        vars.update(verbose_name=verbose_name(self.object), object=self.object)
        kwargs['title'] = mark_safe(self.title % vars)
        return kwargs


class BitcasterBaseListView(BitcasterBaseViewMixin, ListView):
    template_name_base = None

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        vars = dict(kwargs)
        vars.update(verbose_name=verbose_name(self.model))
        kwargs['title'] = mark_safe(self.title % vars)
        return kwargs


class BitcasterBaseCreateView(BitcasterBaseViewMixin, CreateView):
    title = _('Create %(verbose_name)s')


class BitcasterBaseUpdateView(BitcasterBaseViewMixin, BitcasterSingleObjectMixin, UpdateView):
    title = _('Edit %(verbose_name)s')

    def form_valid(self, form):
        self.message_user(_('Changes saved'))
        return super(BitcasterBaseUpdateView, self).form_valid(form)


class BitcasterBaseDeleteView(BitcasterBaseViewMixin, BitcasterSingleObjectMixin, DeleteView):
    template_name = 'bitcaster/generic/confirm_delete.html'
    title = _('Remove %(verbose_name)s')
    user_message = _('Deleted')
    message = _('%(verbose_name)s <strong>%(object)s</strong> will be permanently removed.')

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        vars = dict(verbose_name=verbose_name(self.object),
                    object=self.object)
        kwargs['message'] = mark_safe(self.message % vars)
        return kwargs

    def delete(self, request, *args, **kwargs):
        ret = super().delete(request, *args, **kwargs)
        self.message_user(self.user_message)
        return ret


class BitcasterBaseDetailView(BitcasterBaseViewMixin, DetailView):
    pass


class BitcasterBaseToggleView(MessageUserMixin, SingleObjectMixin, RedirectView):
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.enabled = not obj.enabled
        obj.save()
        op = _('enabled') if obj.enabled else _('disabled')
        self.message_user(f'{obj._meta.verbose_name} {op}')
        return super().get(request, *args, **kwargs)


class PluginInfo(BitcasterTemplateView):
    template_name = 'bitcaster/plugin_info.html'

    def get_context_data(self, **kwargs):
        handler = import_by_name(self.kwargs['fqn'])
        return super().get_context_data(handler=handler, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
