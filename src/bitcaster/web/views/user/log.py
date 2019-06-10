from django.utils.translation import gettext_lazy as _

from bitcaster.models import Notification
from bitcaster.utils.http import get_query_string
from bitcaster.web.views.mixins import NotificationLogMixin
from bitcaster.web.views.organization.mixins import SelectedOrganizationMixin
from bitcaster.web.views.user.base import UserMixin

from ..base import BitcasterBaseListView


class UserNotificationLogView(UserMixin,
                              NotificationLogMixin,
                              SelectedOrganizationMixin, BitcasterBaseListView):
    template_name = 'bitcaster/user/log.html'
    model = Notification
    title = _('Notifications')
    paginate_by = 50

    def get_queryset(self):
        qs = Notification.objects.filter(organization=self.selected_organization,
                                         user=self.request.user)
        qs = self.filter_queryset(qs)
        return qs.order_by('-timestamp')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['filters'] = get_query_string(self.request, remove=['page'])
        data['Notification'] = Notification
        data['active_filter'] = self.active_filter
        return data
