from bitcaster.web.views.application.mixins import SelectedApplicationMixin
from bitcaster.web.views.base import BitcasterBaseListView


class ApplicationTeamList(SelectedApplicationMixin, BitcasterBaseListView):
    template_name = 'bitcaster/application/teams/list.html'
    title = 'Subscribers'

    def get_context_data(self, **kwargs):
        kwargs['pending'] = self.selected_organization.memberships.filter(event=self.selected_event)
        return super().get_context_data(**kwargs)
