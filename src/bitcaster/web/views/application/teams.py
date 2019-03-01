from django.utils.translation import gettext_lazy as _

from bitcaster.models import ApplicationTeam
from bitcaster.web.views.application.mixins import SelectedApplicationMixin
from bitcaster.web.views.base import BitcasterBaseListView


class ApplicationTeamList(SelectedApplicationMixin, BitcasterBaseListView):
    model = ApplicationTeam
    template_name = 'bitcaster/application/teams/list.html'
    title = _('Teams')
