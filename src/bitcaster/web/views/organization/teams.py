import logging

from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext as _

from bitcaster.models import Team
from bitcaster.web.forms import TeamForm
from bitcaster.web.views.base import (BitcasterBaseCreateView,
                                      BitcasterBaseDeleteView,
                                      BitcasterBaseListView,
                                      BitcasterBaseUpdateView,)
from bitcaster.web.views.organization.mixins import OrganizationViewMixin

logger = logging.getLogger(__name__)


class OrganizationTeamMixin(OrganizationViewMixin):
    model = Team
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return self.selected_organization.teams.all()

    def get_context_data(self, **kwargs):
        kwargs['title'] = _('Organization Teams')
        return super().get_context_data(**kwargs)


class OrganizationTeamList(OrganizationTeamMixin, BitcasterBaseListView):
    template_name = 'bitcaster/organization/teams/list.html'


class OrganizationTeamCreate(OrganizationTeamMixin, BitcasterBaseCreateView):
    template_name = 'bitcaster/organization/teams/form.html'
    form_class = TeamForm

    def get_success_url(self):
        return reverse('org-team-list', args=[self.selected_organization.slug])

    def get_initial(self):
        return {'manager': self.request.user}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'organization': self.selected_organization})
        return kwargs

    def form_valid(self, form):
        with transaction.atomic():
            form.instance.organization = self.selected_organization
            self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class OrganizationTeamDelete(OrganizationTeamMixin, BitcasterBaseDeleteView):
    pass


class OrganizationTeamUpdate(OrganizationTeamMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/organization/teams/form.html'
    form_class = TeamForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'organization': self.selected_organization})
        return kwargs

    def get_success_url(self):
        return reverse('org-team-list', args=[self.selected_organization.slug])

    def form_valid(self, form):
        with transaction.atomic():
            self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class OrganizationTeamMember(OrganizationTeamMixin, BitcasterBaseUpdateView):
    fields = ('name',)
    slug_url_kwarg = 'slug'

    def get_success_url(self):
        return reverse('org-team-list', args=[self.selected_organization.slug])

    def get_initial(self):
        return super().get_initial()

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.organization = self.selected_organization
        obj.save()
        return HttpResponseRedirect(self.get_success_url())
