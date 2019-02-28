# -*- coding: utf-8 -*-
import logging

from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  ListView, TemplateView, UpdateView,)
from strategy_field.utils import import_by_name

from .mixins import BitcasterBaseViewMixin, MessageUserMixin

logger = logging.getLogger(__name__)


class BitcasterTemplateView(MessageUserMixin, TemplateView):
    pass


class BitcasterFormView(MessageUserMixin, FormView):
    pass


# class BitcasterSingleObjectTemplateResponseMixin(TemplateResponseMixin):
#
#     def get_context_data(self, **kwargs):
#         return super().get_context_data(opts=self.model._meta, **kwargs)
#     template_name_base = None
    #
    # def get_template_names(self):
    #     try:
    #         if self.template_name is None:
    #             raise ImproperlyConfigured(
    #                 'TemplateResponseMixin requires either a definition of '
    #                 "'template_name' or an implementation of 'get_template_names()'")
    #         names = [self.template_name]
    #     except ImproperlyConfigured:
    #         names = []
    #
    #         # If self.template_name_field is set, grab the value of the field
    #         # of that name from the object; this is the most specific template
    #         # name, if given.
    #         if self.object and self.template_name_field:
    #             name = getattr(self.object, self.template_name_field, None)
    #             if name:
    #                 names.insert(0, name)
    #
    #         if self.template_name_base:
    #             base = 'bitcaster/%s' % self.template_name_base
    #         else:
    #             base = 'bitcaster'
    #
    #         # The least-specific option is the default <app>/<model>_detail.html;
    #         # only use this if the object in question is a model.
    #         if isinstance(self.object, models.Model):
    #             object_meta = self.object._meta
    #             names.append('%s/%s%s.html' % (
    #                 base,
    #                 object_meta.model_name,
    #                 self.template_name_suffix
    #             ))
    #         elif getattr(self, 'model', None) is not None and issubclass(self.model, models.Model):
    #             names.append('%s/%s%s.html' % (
    #                 base,
    #                 self.model._meta.model_name,
    #                 self.template_name_suffix
    #             ))
    #
    #         # If we still haven't managed to find any template names, we should
    #         # re-raise the ImproperlyConfigured to alert the user.
    #         if not names:
    #             raise
    #
    #     return names


class BitcasterBaseListView(BitcasterBaseViewMixin, ListView):
    template_name_base = None

    # def get_template_names(self):
    #     names = []
    #     if self.template_name:
    #         names = [self.template_name]
    #
    #     if hasattr(self.object_list, 'model'):
    #         opts = self.object_list.model._meta
    #         names.append('%s/%s/%s%s.html' % (opts.app_label,
    #                                           self.template_name_base,
    #                                           opts.model_name,
    #                                           self.template_name_suffix))
    #     elif not names:
    #         raise ImproperlyConfigured(
    #             "%(cls)s requires either a 'template_name' attribute "
    #             'or a get_queryset() method that returns a QuerySet.' % {
    #                 'cls': self.__class__.__name__,
    #             }
    #         )
    #     return names


class BitcasterBaseCreateView(BitcasterBaseViewMixin, CreateView):
    template_name_suffix = '_edit'


class BitcasterBaseUpdateView(BitcasterBaseViewMixin, UpdateView):
    template_name_suffix = '_edit'


class BitcasterBaseDeleteView(BitcasterBaseViewMixin, DeleteView):
    template_name = 'bitcaster/generic/confirm_delete.html'


class BitcasterBaseDetailView(BitcasterBaseViewMixin, DetailView):
    pass


class PluginInfo(BitcasterTemplateView):
    template_name = 'bitcaster/plugin_info.html'

    def get_context_data(self, **kwargs):
        handler = import_by_name(self.kwargs['fqn'])
        return super().get_context_data(handler=handler, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
