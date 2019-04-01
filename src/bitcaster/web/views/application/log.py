from django.utils.translation import gettext as _

from bitcaster.models.counters import LogEntry
from bitcaster.web.views.application.mixins import SelectedApplicationMixin
from bitcaster.web.views.base import BitcasterBaseListView


class ApplicationLog(SelectedApplicationMixin, BitcasterBaseListView):
    template_name = 'bitcaster/application/log.html'
    model = LogEntry
    title = _('Log')

    def get_queryset(self):
        return LogEntry.objects.filter(application=self.selected_application)
