from django.urls import reverse
from django.utils.translation import gettext as _

from bitcaster.models import Subscription
from bitcaster.utils.http import get_query_string
from bitcaster.web.forms.subscription import EventSubscriptionEditForm
from bitcaster.web.views.application.mixins import SelectedApplicationMixin
from bitcaster.web.views.base import (BitcasterBaseListView,
                                      BitcasterBaseUpdateView,)
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


class ApplicationSubscriptionEdit(SelectedApplicationMixin, BitcasterBaseUpdateView):
    model = Subscription
    template_name = 'bitcaster/application/subscriptions/form.html'
    pk_url_kwarg = 'subscription'
    form_class = EventSubscriptionEditForm

    def get_context_data(self, **kwargs):
        return super().get_context_data(from_=self.request.GET.get('from'),
                                        **kwargs)

    def get_success_url(self):
        _from = self.request.GET.get('from')
        if _from == 'app':
            return reverse('app-subscriptions', args=[self.selected_organization.slug,
                                                      self.selected_application.slug])
        elif _from == 'event':
            return reverse('app-event-subscriptions',
                           args=[self.selected_organization.slug,
                                 self.selected_application.slug,
                                 self.object.event.pk]
                           )
        return self.request.META.get('HTTP_REFERER')

    def get_queryset(self):
        qs = Subscription.objects.filter(event__application=self.selected_application)
        qs = qs.select_related('event__application', 'channel', 'subscriber')
        return qs
