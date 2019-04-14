from django.utils.translation import gettext as _

from bitcaster.models import Notification
from bitcaster.utils.http import get_query_string
from bitcaster.web.views.mixins import FilterQuerysetMixin

from ..base import BitcasterBaseListView
from .mixins import SelectedOrganizationMixin


class OrganizationNotificationLogView(FilterQuerysetMixin,
                                      SelectedOrganizationMixin, BitcasterBaseListView):
    template_name = 'bitcaster/organization/log.html'
    model = Notification
    title = _('Notification Log')
    paginate_by = 50
    filter_fieldmap = {'channel': 'channel__name__iexact',
                       'application': 'application__name__istartswith',
                       'event': 'event__name__istartswith',
                       'user': 'subscription__subscriber__email__istartswith',
                       'subscriber': 'subscription__subscriber__email__istartswith',
                       }

    def get_queryset(self):
        qs = Notification.objects.filter(application__organization=self.selected_organization)
        qs = self.filter_queryset(qs)
        return qs.order_by('-timestamp')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['filters'] = get_query_string(self.request, remove=['page'])
        return data
