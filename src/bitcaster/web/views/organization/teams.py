# import logging
#
# from django.db import transaction
# from django.http import HttpResponseRedirect
#
# from bitcaster.models import Team
# from bitcaster.web.forms import TeamForm
# from bitcaster.web.views.base import (BitcasterBaseCreateView,
#                                       BitcasterBaseDeleteView,
#                                       BitcasterBaseListView,
#                                       BitcasterBaseUpdateView,)
#
# from .org import OrganizationBaseView
#
# logger = logging.getLogger(__name__)
#
#
# class TeamMixin(OrganizationBaseView):
#     model = Team
#     slug_url_kwarg = 'slug'
#     # title = _('Teams')
#
#     def get_queryset(self):
#         return self.selected_organization.teams.all()
#
#     def get_success_url(self):
#         return self.selected_organization.urls.teams
#
#
# class OrganizationTeamList(TeamMixin, BitcasterBaseListView):
#     template_name = 'bitcaster/organization/team/list.html'
#
#
# class OrganizationTeamCreate(TeamMixin, BitcasterBaseCreateView):
#     template_name = 'bitcaster/organization/team/form.html'
#     form_class = TeamForm
#
#     def get_initial(self):
#         return {'manager': self.request.user}
#
#     def form_valid(self, form):
#         with transaction.atomic():
#             form.instance.organization = self.selected_organization
#             self.object = form.save()
#         return HttpResponseRedirect(self.get_success_url())
#
#
# class OrganizationTeamDelete(TeamMixin, BitcasterBaseDeleteView):
#     pass
#     # title = _('Remove Team')
#
#
# class OrganizationTeamUpdate(TeamMixin, BitcasterBaseUpdateView):
#     template_name = 'bitcaster/organization/team/form.html'
#     form_class = TeamForm
#     # title = _('Edit Team')
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs.update({'organization': self.selected_organization})
#         return kwargs
#
#     def form_valid(self, form):
#         with transaction.atomic():
#             self.object = form.save()
#         return HttpResponseRedirect(self.get_success_url())
#
#
# class OrganizationTeamMember(TeamMixin, BitcasterBaseUpdateView):
#     fields = ('name',)
#     slug_url_kwarg = 'slug'
#
#     def form_valid(self, form):
#         obj = form.save(commit=False)
#         obj.organization = self.selected_organization
#         obj.save()
#         return HttpResponseRedirect(self.get_success_url())
