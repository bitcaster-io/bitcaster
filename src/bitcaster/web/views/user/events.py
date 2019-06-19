from django.utils.translation import gettext as _

from bitcaster.models import Event, User
from bitcaster.web.views.base import BitcasterBaseListView
from bitcaster.web.views.user.base import UserMixin


class UserEventMixin(UserMixin):
    model = User
    title = _('Events')

    def get_queryset(self):
        return Event.objects.all()


class UserEventListView(UserEventMixin, BitcasterBaseListView):
    template_name = 'bitcaster/user/events.html'

    def get_queryset(self):
        filters = {'core': False,
                   'subscription_policy': Event.POLICIES.FREE}
        return super().get_queryset().filter(**filters).order_by('application__name',
                                                                 'name')

    def get_context_data(self, **kwargs):
        subscripted_events = self.request.user.subscriptions.values_list('event__pk', flat=True).distinct()
        return super().get_context_data(subscripted_events=subscripted_events,
                                        **kwargs)
