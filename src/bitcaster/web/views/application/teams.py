import logging

from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import ModelFormMixin
from sentry_sdk import capture_exception

from bitcaster.models import ApplicationTeam
from bitcaster.utils.http import get_query_string
from bitcaster.web.forms import ApplicationTeamForm
from bitcaster.web.forms.team import ApplicationTeamAddMemberForm
from bitcaster.web.views.base import (BitcasterBaseCreateView,
                                      BitcasterBaseDeleteView,
                                      BitcasterBaseListView,
                                      BitcasterBaseUpdateView,)

from .app import SelectedApplicationMixin

logger = logging.getLogger(__name__)


class TeamMixin(SelectedApplicationMixin):
    model = ApplicationTeam
    pk_url_kwarg = 'team'

    def get_queryset(self):
        return self.selected_application.teams.all()

    def get_success_url(self):
        return self.selected_application.urls.teams


class SelectedTeamMixin(TeamMixin):

    @cached_property
    def selected_team(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return self.selected_application.teams.get(pk=pk)

    def get_context_data(self, **kwargs):
        return super().get_context_data(team=self.selected_team,
                                        team_name=self.selected_team.name,
                                        **kwargs)


class ApplicationTeamFormMixin(ModelFormMixin):
    form_class = ApplicationTeamForm
    form_show_labels = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'application': self.selected_application})
        return kwargs

    def form_valid(self, form):
        form.instance.application = self.selected_application
        return super().form_valid(form)


class ApplicationTeamList(TeamMixin, BitcasterBaseListView):
    template_name = 'bitcaster/application/team/list.html'


class ApplicationTeamCreate(TeamMixin, ApplicationTeamFormMixin, BitcasterBaseCreateView):
    template_name = 'bitcaster/application/team/create.html'
    form_class = ApplicationTeamForm

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            manager_autocomplete_url=reverse('app-member-autocomplete',
                                             args=[self.selected_organization.slug,
                                                   self.selected_application.slug]
                                             ),
            **kwargs)

    #
    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs.update({'application': self.selected_application})
    #     return kwargs

    def form_valid(self, form):
        with transaction.atomic():
            form.instance.application = self.selected_application
            self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class ApplicationTeamDelete(TeamMixin, BitcasterBaseDeleteView):
    pass


#
# class ApplicationTeamUpdate(TeamMixin, BitcasterBaseUpdateView):
#     template_name = 'bitcaster/application/team/edit.html'
#     form_class = ApplicationTeamForm
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs.update({'application': self.selected_application})
#         return kwargs
#
#     def form_valid(self, form):
#         with transaction.atomic():
#             self.object = form.save()
#         return HttpResponseRedirect(self.get_success_url())
#
#
# class ApplicationTeamMember(TeamMixin, BitcasterBaseUpdateView):
#     fields = ('name',)
#     slug_url_kwarg = 'slug'
#
#     def form_valid(self, form):
#         obj = form.save(commit=False)
#         obj.application = self.selected_application
#         obj.save()
#         return HttpResponseRedirect(self.get_success_url())


class ApplicationTeamUpdate(SelectedTeamMixin, ApplicationTeamFormMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/application/team/edit.html'

    # def get_object(self, queryset=None):
    #     pk = self.kwargs.get(self.pk_url_kwarg)
    #     return self.selected_application.teams.get(pk=pk)


class ApplicationTeamMemberRemove(SelectedTeamMixin, BitcasterBaseDeleteView):
    message = _('User <strong>%(object)s</strong> will be removed from team %(team_name)s')
    user_message = _('User removed')
    title = _('Remove user from group')

    def get_object(self, queryset=None):
        return self.selected_team.members.get(pk=self.kwargs.get('member'))

    def get_success_url(self):
        return reverse('app-team-members', args=[self.selected_organization.slug,
                                                 self.selected_application.slug,
                                                 self.selected_team.pk
                                                 ])


class ApplicationTeamMember(SelectedTeamMixin, BitcasterBaseListView):
    title = _('%(team_name)s members')
    template_name = 'bitcaster/application/team/members.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(form=ApplicationTeamAddMemberForm(),
                                        filters=get_query_string(self.request, remove=['page']),
                                        member_automplete_url=reverse('app-member-autocomplete',
                                                                      args=[
                                                                          self.selected_organization.slug,
                                                                          self.selected_application.slug
                                                                      ]),
                                        **kwargs)

    def post(self, request, *args, **kwargs):
        form = ApplicationTeamAddMemberForm(data=request.POST)
        if form.is_valid():
            try:
                pk = form.cleaned_data['user']
                user = self.selected_organization.memberships.get(user__id=pk)
                self.selected_team.members.add(user)
            except Exception:
                capture_exception()

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = self.selected_team.members.all()
        target = self.request.GET.get('filter')
        if target:
            qs = qs.filter(email__istartswith=target)
        return qs
