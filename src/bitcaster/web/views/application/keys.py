import logging

from bitcaster.models import ApplicationTriggerKey
from bitcaster.web.forms import ApplicationTriggerKeyForm
from bitcaster.web.views.application.app import ApplicationViewMixin
from bitcaster.web.views.base import (BitcasterBaseCreateView,
                                      BitcasterBaseDeleteView,
                                      BitcasterBaseListView,
                                      BitcasterBaseUpdateView,)

logger = logging.getLogger(__name__)


class KeyMixin(ApplicationViewMixin):
    form_class = ApplicationTriggerKeyForm
    model = ApplicationTriggerKey

    def get_queryset(self):
        return self.selected_application.keys.all()

    def get_success_url(self):
        return self.selected_application.urls.keys

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'application': self.selected_application})
        return kwargs


class ApplicationKeyList(KeyMixin, BitcasterBaseListView):
    template_name = 'bitcaster/application/keys/list.html'
    # title = _('Application Keys')


class ApplicationKeyCreate(KeyMixin, BitcasterBaseCreateView):
    template_name = 'bitcaster/application/keys/form.html'


class ApplicationKeyUpdate(KeyMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/application/keys/form.html'


class ApplicationKeyDelete(KeyMixin, BitcasterBaseDeleteView):
    pass
