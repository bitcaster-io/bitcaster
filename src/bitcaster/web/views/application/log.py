from django.utils.translation import gettext as _

from bitcaster.models import AuditLogEntry, Notification
from bitcaster.utils.http import get_query_string
from bitcaster.web.views.application.mixins import SelectedApplicationMixin
from bitcaster.web.views.base import BitcasterBaseListView
from bitcaster.web.views.mixins import FilterQuerysetMixin, NotificationLogMixin


class ApplicationAuditLog(FilterQuerysetMixin,
                          SelectedApplicationMixin, BitcasterBaseListView):
    template_name = 'bitcaster/application/auditlog.html'
    model = AuditLogEntry
    title = _('Audit Log')
    paginate_by = 50

    # filter_fieldmap = {'channel': 'channel__name__iexact',
    #                    'application': 'application__name__istartswith',
    #                    'event': 'event__name__istartswith',
    #                    'user': 'subscription__subscriber__email__istartswith',
    #                    'subscriber': 'subscription__subscriber__email__istartswith'}

    def get_queryset(self):
        qs = AuditLogEntry.objects.filter(application=self.selected_application)
        qs = self.filter_queryset(qs)
        return qs.order_by('-timestamp')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['filters'] = get_query_string(self.request, remove=['page'])
        return data


class ApplicationNotificationLog(NotificationLogMixin,
                                 SelectedApplicationMixin, BitcasterBaseListView):
    template_name = 'bitcaster/application/log.html'
    model = Notification
    title = _('Notification Log')

    def get_queryset(self):
        qs = Notification.objects.filter(application=self.selected_application)
        qs = self.filter_queryset(qs)
        return qs.order_by('-timestamp')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['filters'] = get_query_string(self.request, remove=['page'])
        return data
