from dal_select2.views import Select2QuerySetView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from bitcaster.models import Channel, OrganizationMember
from bitcaster.web.views.application.mixins import SelectedApplicationMixin
from bitcaster.web.views.organization.mixins import SelectedOrganizationMixin


class UserAutocomplete(LoginRequiredMixin, Select2QuerySetView):
    def get_queryset(self):
        qs = OrganizationMember.objects.all()

        if self.q:
            qs = qs.filter(user__email__istartswith=self.q)

        return qs


class ChannelAutocomplete(LoginRequiredMixin, Select2QuerySetView):
    def get_queryset(self):
        qs = Channel.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class AddressAutocomplete(LoginRequiredMixin, Select2QuerySetView):
    def get_queryset(self):
        qs = self.request.user.addresses.all()

        if self.q:
            qs = qs.filter(label__istartswith=self.q)

        return qs


class ApplicationAutocomplete(SelectedOrganizationMixin, Select2QuerySetView):
    def get_queryset(self):
        qs = self.selected_organization.applications.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class OrganizationMembersAutocomplete(SelectedOrganizationMixin, Select2QuerySetView):
    permissions = ['manage_organization', 'manage_application']

    def get_queryset(self):
        qs = self.selected_organization.members.all()

        if self.q:
            qs = qs.filter(email__istartswith=self.q)

        return qs


class ApplicationMembersAutocomplete(SelectedApplicationMixin, Select2QuerySetView):
    def get_queryset(self):
        qs = self.selected_application.members.all()

        if self.q:
            qs = qs.filter(Q(name__istartswith=self.q) |
                           Q(friendly_name__istartswith=self.q) |
                           Q(email__istartswith=self.q))

        return qs


class ApplicationCandidateAutocomplete(SelectedApplicationMixin, Select2QuerySetView):
    def get_queryset(self):
        # returns all organization members not already part of selected application
        qs = self.selected_organization.memberships.exclude(applications__application=self.selected_application)

        if self.q:
            qs = qs.filter(Q(user__name__istartswith=self.q) |
                           Q(user__friendly_name__istartswith=self.q) |
                           Q(user__email__istartswith=self.q))

        return qs
