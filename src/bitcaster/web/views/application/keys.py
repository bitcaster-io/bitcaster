# -*- coding: utf-8 -*-
import logging

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from bitcaster.models import ApplicationTriggerKey
from bitcaster.web.forms import ApplicationTriggerKeyForm
from bitcaster.web.views.application.app import ApplicationViewMixin
from bitcaster.web.views.base import (BitcasterBaseCreateView,
                                      BitcasterBaseDeleteView,
                                      BitcasterBaseListView,
                                      BitcasterBaseUpdateView,)

logger = logging.getLogger(__name__)


class ApplicationKeyList(ApplicationViewMixin, BitcasterBaseListView):
    template_name = 'bitcaster/application/keys/list.html'

    def get_queryset(self):
        return self.selected_application.keys.all()

    def get_context_data(self, **kwargs):
        kwargs['title'] = _('Application Keys')
        return super().get_context_data(**kwargs)


class ApplicationKeyFormMixin:
    form_class = ApplicationTriggerKeyForm
    model = ApplicationTriggerKey
    template_name = 'bitcaster/application/keys/form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'application': self.selected_application})
        return kwargs

    def get_success_url(self):
        return reverse('app-key-list', args=[self.selected_organization.slug,
                                             self.selected_application.slug])


class ApplicationKeyCreate(ApplicationKeyFormMixin, ApplicationViewMixin,
                           BitcasterBaseCreateView):
    pass


class ApplicationKeyUpdate(ApplicationViewMixin, ApplicationKeyFormMixin, BitcasterBaseUpdateView):

    def get_queryset(self):
        return self.selected_application.keys.all()

    def get_context_data(self, **kwargs):
        kwargs['title'] = _('Application Keys')
        return super().get_context_data(**kwargs)


class ApplicationKeyDelete(ApplicationViewMixin, BitcasterBaseDeleteView):
    pk_url_kwarg = 'pk'
    template_name = 'bitcaster/application/keys/confirm_delete.html'

    def get_object(self, queryset=None):
        return self.selected_application.keys.get(pk=self.kwargs.get(self.pk_url_kwarg))

    def get_success_url(self):
        return reverse('app-key-list', args=[self.selected_organization.slug,
                                             self.selected_application.slug])
