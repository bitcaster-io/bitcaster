from django.utils.translation import gettext as _

from bitcaster.models.audit import AuditLogEntry
from bitcaster.utils.http import get_query_string
from bitcaster.web.views.base import BitcasterBaseListView
from bitcaster.web.views.mixins import FilterQuerysetMixin
from bitcaster.web.views.organization.mixins import SelectedOrganizationMixin


class OrganizationAuditLogView(FilterQuerysetMixin,
                               SelectedOrganizationMixin, BitcasterBaseListView):
    template_name = 'bitcaster/organization/auditlog.html'
    model = AuditLogEntry
    title = _('Audit Log')
    paginate_by = 50
    filter_fieldmap = {'actor': 'actor_label__istartswith',
                       'target': 'target_label__istartswith',
                       # 'event': 'event__istartswith',
                       }

    def get_queryset(self):
        qs = AuditLogEntry.objects.filter(organization=self.selected_organization)
        qs = self.filter_queryset(qs)
        return qs.order_by('-timestamp')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['filters'] = get_query_string(self.request, remove=['page'])
        return data
