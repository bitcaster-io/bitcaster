from django.utils.translation import gettext as _

from bitcaster.models import Subscription
from bitcaster.utils.http import get_query_string
from bitcaster.web.views.application.mixins import SelectedApplicationMixin
from bitcaster.web.views.base import BitcasterBaseListView
from bitcaster.web.views.mixins import FilterQuerysetMixin


class ApplicationSubscriptionList(SelectedApplicationMixin, FilterQuerysetMixin,
                                  BitcasterBaseListView):
    model = Subscription
    template_name = 'bitcaster/application/subscriptions/list.html'
    paginate_by = 50

    search_fields = ['subscriber__name__istartswith']
    filter_fieldmap = {
        # Translators: UserNotificationLogView.filter_fieldmap
        _('channel'): 'channel__name__istartswith',
        _('event'): 'event__name__istartswith',
        _('enabled'): '_parse_bool',
    }

    def get_context_data(self, **kwargs):
        kwargs['pending'] = self.selected_application.invitations.filter()
        kwargs['filters'] = get_query_string(self.request, remove=['page'])
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        qs = Subscription.objects.filter(event__application=self.selected_application)
        qs = qs.select_related('event__application', 'channel', 'subscriber')
        qs = self.filter_queryset(qs)
        return qs.order_by('event', 'subscriber', 'channel')
