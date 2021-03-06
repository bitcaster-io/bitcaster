import time

from django.db.models import Count, Q
from django.utils.translation import gettext as _

from bitcaster.models import Event
from bitcaster.utils.http import get_query_string
from bitcaster.web.views.base import BitcasterBaseListView
from bitcaster.web.views.mixins import FilterQuerysetMixin
from bitcaster.web.views.user.base import UserMixin


class UserEventListView(UserMixin, FilterQuerysetMixin, BitcasterBaseListView):
    template_name = 'bitcaster/user/events.html'
    search_fields = ['application__name__istartswith', 'name__istartswith']
    model = Event
    title = _('Events')

    filter_fieldmap = {
        # Translators: UserEventListView.filter_fieldmap
        _('application'): 'application__name__iexact',
        _('event'): 'name__icontains',
    }

    def get_queryset(self):
        filters = {'core': False,
                   'subscription_policy': Event.POLICIES.FREE}
        qs = Event.objects.filter(**filters)
        qs = qs.select_related('application')
        qs = qs.order_by('application__name', 'name')
        qs = self.filter_queryset(qs).annotate(c=Count('subscriptions',
                                                       filter=Q(subscriptions__subscriber=self.request.user)
                                                       ))
        return qs

    def get_context_data(self, **kwargs):
        # subscripted_events = self.request.user.subscriptions.values_list('event__pk', flat=True).distinct()
        data = super().get_context_data(**kwargs)
        data['filters'] = get_query_string(self.request, remove=['page'])
        data['version'] = time.time()
        return data
