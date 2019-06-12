import logging

from django.urls import reverse
from django.utils.translation import ugettext as _
from django.views.generic import RedirectView

from bitcaster.models import Application, AuditEvent
from bitcaster.web.forms import ApplicationForm
from bitcaster.web.views.mixins import LogAuditMixin, MessageUserMixin

from ..base import (BitcasterBaseDeleteView, BitcasterBaseDetailView,
                    BitcasterBaseUpdateView,)
from .mixins import SelectedApplicationMixin

logger = logging.getLogger(__name__)


class ApplicationViewMixin(LogAuditMixin, MessageUserMixin, SelectedApplicationMixin):
    model = Application
    slug_url_kwarg = 'app'


class ApplicationUpdateView(ApplicationViewMixin, BitcasterBaseUpdateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'bitcaster/application/form.html'

    def get_success_url(self):
        return self.selected_application.urls.edit

    def form_valid(self, form):
        ret = super().form_valid(form)
        self.audit(self.object, AuditEvent.APPLICATION_UPDATED)
        self.message_user(_('Application updated'))
        return ret


class ApplicationDashboard(ApplicationViewMixin, BitcasterBaseDetailView):
    template_name = 'bitcaster/application/dashboard.html'

    @property
    def title(self):
        return self.object.name

    def get_context_data(self, **kwargs):
        # app = self.get_object()
        # org = app.organization
        # cache_key = f'org:app:dashboard:{app.pk}'
        kwargs['occurences'] = self.selected_application.occurences.active()

        return super().get_context_data(**kwargs)


class ApplicationDeleteView(ApplicationViewMixin, BitcasterBaseDeleteView):

    def get_success_url(self):
        return reverse('org-applications', args=[self.selected_organization.slug])

    def delete(self, request, *args, **kwargs):
        ret = super().delete(request, *args, **kwargs)
        self.audit(self.object, AuditEvent.APPLICATION_DELETED)
        self.message_user(_('Application deleted'))
        return ret


class ApplicationCheckConfigView(ApplicationViewMixin, RedirectView):
    pattern_name = 'app-dashboard'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ApplicationDetail(ApplicationViewMixin, BitcasterBaseDetailView):
    pass
