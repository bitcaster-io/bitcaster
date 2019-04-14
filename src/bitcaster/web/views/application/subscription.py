from bitcaster.models import Subscription
from bitcaster.web.views.application.mixins import SelectedApplicationMixin
from bitcaster.web.views.base import BitcasterBaseListView


class ApplicationSubscriptionList(SelectedApplicationMixin, BitcasterBaseListView):
    model = Subscription
    template_name = 'bitcaster/application/subscriptions/list.html'

    def get_context_data(self, **kwargs):
        kwargs['pending'] = self.selected_application.invitations.filter()
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        # return self.selected_application.events.order_by('')
        return Subscription.objects.filter(event__application=self.selected_application).order_by('event', 'subscriber',
                                                                                                  'channel')
