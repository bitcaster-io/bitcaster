import logging

from django.db import transaction
from django.http import HttpResponseRedirect

from bitcaster.models import Team
from bitcaster.web.forms import TeamForm
from bitcaster.web.views.base import (BitcasterBaseCreateView,
                                      BitcasterBaseDeleteView,
                                      BitcasterBaseListView,
                                      BitcasterBaseUpdateView,)

from .app import SelectedApplicationMixin

logger = logging.getLogger(__name__)


class TeamMixin(SelectedApplicationMixin):
    model = Team
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return self.selected_application.teams.all()

    def get_success_url(self):
        return self.selected_application.urls.teams


class ApplicationTeamList(TeamMixin, BitcasterBaseListView):
    template_name = 'bitcaster/application/team/list.html'


class ApplicationTeamCreate(TeamMixin, BitcasterBaseCreateView):
    template_name = 'bitcaster/application/team/form.html'
    form_class = TeamForm

    def get_initial(self):
        return {'manager': self.request.user}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'application': self.selected_application})
        return kwargs

    def form_valid(self, form):
        with transaction.atomic():
            form.instance.application = self.selected_application
            self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class ApplicationTeamDelete(TeamMixin, BitcasterBaseDeleteView):
    pass


class ApplicationTeamUpdate(TeamMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/application/team/form.html'
    form_class = TeamForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'application': self.selected_application})
        return kwargs

    def form_valid(self, form):
        with transaction.atomic():
            self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class ApplicationTeamMember(TeamMixin, BitcasterBaseUpdateView):
    fields = ('name',)
    slug_url_kwarg = 'slug'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.application = self.selected_application
        obj.save()
        return HttpResponseRedirect(self.get_success_url())
