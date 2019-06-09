from django.utils.translation import gettext as _

from bitcaster.models import Notification
from bitcaster.utils.http import get_query_string
from bitcaster.web.views.mixins import FilterQuerysetMixin
from bitcaster.web.views.organization.mixins import SelectedOrganizationMixin
from bitcaster.web.views.user.base import UserMixin

from ..base import BitcasterBaseListView


class UserNotificationLogView(UserMixin,
                              FilterQuerysetMixin,
                              SelectedOrganizationMixin, BitcasterBaseListView):
    template_name = 'bitcaster/user/log.html'
    model = Notification
    title = _('Notifications')
    paginate_by = 50
    filter_fieldmap = {'channel': 'channel__name__iexact',
                       'occurence': 'occurence_id',
                       '#': 'occurence_id',
                       'application': 'application__name__istartswith',
                       'event': 'event__name__istartswith',
                       'status': '_filter_status',
                       'user': 'subscription__subscriber__email__istartswith',
                       'subscriber': 'subscription__subscriber__email__istartswith',
                       }

    def _filter_status(self, parser, keyword, value):
        code = [c[0] for c in Notification.STATUSES if c[1].lower() == value]
        parser.kwargs[keyword] = code[0]

    def get_queryset(self):
        qs = Notification.objects.filter(application__organization=self.selected_organization)
        qs = self.filter_queryset(qs)
        return qs.order_by('-timestamp')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['filters'] = get_query_string(self.request, remove=['page'])
        data['Notification'] = Notification
        return data
