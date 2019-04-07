from django.utils.translation import gettext as _

from bitcaster.models.counters import LogEntry
from bitcaster.utils.http import get_query_string
from bitcaster.web.views.application.mixins import SelectedApplicationMixin
from bitcaster.web.views.base import BitcasterBaseListView


class ApplicationLog(SelectedApplicationMixin, BitcasterBaseListView):
    template_name = 'bitcaster/application/log.html'
    model = LogEntry
    title = _('Log')
    paginate_by = 50

    def get_queryset(self):
        qs = LogEntry.objects.filter(application=self.selected_application)
        target = self.request.GET.get('filter')
        if target:
            qs = qs.filter(org_member__user__email__istartswith=target)
        return qs.order_by('-timestamp')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['filters'] = get_query_string(self.request, remove=['page'])
        return data
