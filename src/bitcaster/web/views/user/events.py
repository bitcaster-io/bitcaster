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
        return super().get_queryset().filter(core=False).order_by('application__name', 'name')
        # return super().get_queryset().exclude(subscriptions__subscriber=self.request.user,
        #                                       subscriptions__isnull=False).order_by('application__name', 'name')

#
# class UserEventSubcribe(UserEventMixin, LogAuditMixin, BitcasterBaseCreateView):
#     template_name = 'bitcaster/user/subscribe.html'
#     title = 'Event %(object)s'
#     form_class = UserSubscribeForm
#
#     def get_success_url(self):
#         return reverse('user-events', args=[self.selected_organization.slug])
#
#     def get_object(self, queryset=None):
#         return self.get_queryset().get(id=self.kwargs['pk'])
#
#     def get_context_data(self, **kwargs):
#         self.object = self.get_object()
#         ret = super().get_context_data(object=self.object, **kwargs)
#         ret['not_usable_channels'] = self.object.channels.exclude(assignments__user=self.request.user,
#                                                                   assignments__verified=True)
#         ret['usable_channels'] = self.object.channels.all()
#         return ret
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['instance'] = self.get_object()
#         kwargs['user'] = self.request.user
#         return kwargs
#
#     def form_valid(self, form):
#         selection = form.cleaned_data['addresses']
#         for a in self.request.user.assignments.filter(id__in=selection):
#             obj, __ = Subscription.objects.get_or_create(subscriber=self.request.user,
#                                                          address=a.address,
#                                                          channel=a.channel,
#                                                          event=form.event,
#                                                          defaults={'trigger_by': self.request.user,
#                                                                    'enabled': a.verified,
#                                                                    'status': Subscription.STATUSES.OWNED})
#             self.audit(obj, AuditLogEntry.AuditEvent.SUBSCRIPTION_CREATED)
#
#         return HttpResponseRedirect(self.get_success_url())
