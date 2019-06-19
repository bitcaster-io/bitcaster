from django.utils.translation import gettext as _

from bitcaster.models import Notification
from bitcaster.utils.http import get_query_string
from bitcaster.web.views.mixins import NotificationLogMixin

from ..base import BitcasterBaseListView
from .mixins import SelectedOrganizationMixin


class OrganizationNotificationLogView(NotificationLogMixin,
                                      SelectedOrganizationMixin, BitcasterBaseListView):
    template_name = 'bitcaster/organization/log.html'
    model = Notification
    title = _('Notification Log')

    def get_queryset(self):
        qs = Notification.objects.filter(organization=self.selected_organization)
        qs = self.filter_queryset(qs)
        return qs.order_by('-timestamp')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['filters'] = get_query_string(self.request, remove=['page'])
        data['Notification'] = Notification
        return data
