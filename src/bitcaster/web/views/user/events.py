from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext as _

from bitcaster.models import Event, Subscription, User
from bitcaster.models.audit import AuditLogEntry
from bitcaster.web.forms.user import UserSubscribeForm
from bitcaster.web.views.base import (BitcasterBaseCreateView,
                                      BitcasterBaseListView,)
from bitcaster.web.views.user.base import LogAuditMixin, UserMixin


class UserEventMixin(UserMixin):
    model = User
    title = _('Events')

    def get_queryset(self):
        return Event.objects.all()


class UserEventListView(UserEventMixin, BitcasterBaseListView):
    template_name = 'bitcaster/user/events.html'

    def get_queryset(self):
        return super().get_queryset().exclude(subscriptions__subscriber=self.request.user,
                                              subscriptions__isnull=False).order_by('application__name', 'name')


class UserEventSubcribe(UserEventMixin, LogAuditMixin, BitcasterBaseCreateView):
    template_name = 'bitcaster/user/subscribe.html'
    title = 'Event %(object)s'
    form_class = UserSubscribeForm

    def get_success_url(self):
        return reverse('user-events', args=[self.selected_organization.slug])

    def get_object(self, queryset=None):
        return self.get_queryset().get(id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        ret = super().get_context_data(object=self.object, **kwargs)
        ret['not_usable_channels'] = self.object.channels.exclude(addresses__user=self.request.user,
                                                                  addresses__address__verified=True)
        ret['usable_channels'] = self.object.channels.filter(addresses__user=self.request.user,
                                                             addresses__address__verified=True)
        return ret

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs

    def form_valid(self, form):
        for channel in form.cleaned_data['channels']:
            obj = Subscription.objects.create(subscriber=self.request.user,
                                              trigger_by=self.request.user,
                                              event=form.event,
                                              channel=channel,
                                              enabled=True,
                                              status=Subscription.STATUSES.OWNED)
            self.audit(event=AuditLogEntry.AuditEvent.MEMBER_SUBSCRIBE_EVENT,
                       target_object=obj.pk,
                       target_label=str(obj))

        return HttpResponseRedirect(self.get_success_url())
