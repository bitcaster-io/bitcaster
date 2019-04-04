import logging

from django.core.cache import cache
from django.urls import reverse
from django.views.generic import RedirectView

from bitcaster.models import Application
from bitcaster.web.forms import ApplicationForm

from ..base import (BitcasterBaseDeleteView, BitcasterBaseDetailView,
                    BitcasterBaseUpdateView,)
from .mixins import SelectedApplicationMixin

logger = logging.getLogger(__name__)


class ApplicationViewMixin(SelectedApplicationMixin):
    model = Application
    slug_url_kwarg = 'app'


class ApplicationUpdateView(ApplicationViewMixin, BitcasterBaseUpdateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'bitcaster/application/form.html'

    def get_success_url(self):
        return self.selected_application.urls.edit


class ApplicationDashboard(ApplicationViewMixin, BitcasterBaseDetailView):
    template_name = 'bitcaster/application/dashboard.html'

    @property
    def title(self):
        return self.object.name

    def get_context_data(self, **kwargs):
        app = self.get_object()
        org = app.organization
        cache_key = f'org:app:dashboard:{app.pk}'
        org_data = cache.get(cache_key, version=app.version)
        if not org_data:
            org_data = {'active_users': org.members.count(),
                        'pending_users': org.invitations.count(),
                        'enabled_channels': app.channels.filter(enabled=True).count(),
                        'disabled_channels': app.channels.filter(enabled=False).count(),
                        'enabled_events': app.events.filter(enabled=True).count(),
                        'disabled_events': app.events.filter(enabled=False).count(),
                        'enabled_keys': app.keys.filter(enabled=True).count(),
                        'disabled_keys': app.keys.filter(enabled=False).count(),
                        'access_all_events_keys': app.keys.filter(all_events=True).count(),
                        }
            # org_data['box_channels'] = app.issues.get_tag_for('channels')
            # org_data['box_events'] = app.issues.get_tag_for('events')
            # org_data['box_keys'] = app.issues.get_tag_for('keys')
            cache.set(cache_key, org_data)
        kwargs['data'] = org_data
        return super().get_context_data(**kwargs)


class ApplicationDeleteView(ApplicationViewMixin, BitcasterBaseDeleteView):

    def get_success_url(self):
        return reverse('org-applications', args=[self.selected_organization.slug])


class ApplicationCheckConfigView(ApplicationViewMixin, RedirectView):
    pattern_name = 'app-dashboard'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ApplicationDetail(ApplicationViewMixin, BitcasterBaseDetailView):
    pass
