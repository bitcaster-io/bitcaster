from dal_select2.views import Select2QuerySetView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from bitcaster.models import OrganizationMember
from bitcaster.web.views.application.mixins import SelectedApplicationMixin
from bitcaster.web.views.organization.mixins import SelectedOrganizationMixin


class UserAutocomplete(LoginRequiredMixin, Select2QuerySetView):
    def get_queryset(self):
        qs = OrganizationMember.objects.all()

        if self.q:
            qs = qs.filter(user__email__istartswith=self.q)

        return qs.order_by('user__email')


class ChannelAutocomplete(SelectedOrganizationMixin, LoginRequiredMixin, Select2QuerySetView):
    permissions = None

    def get_queryset(self):
        qs = self.selected_organization.channels.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs.order_by('name')


class AddressAutocomplete(LoginRequiredMixin, Select2QuerySetView):
    def get_queryset(self):
        qs = self.request.user.addresses.all()

        if self.q:
            qs = qs.filter(Q(label__icontains=self.q) | Q(address__icontains=self.q))

        return qs.order_by('label')


class ApplicationAutocomplete(SelectedOrganizationMixin, Select2QuerySetView):
    def get_queryset(self):
        qs = self.selected_organization.applications.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs.order_by('name')


class OrganizationMembersAutocomplete(SelectedOrganizationMixin, Select2QuerySetView):
    permissions = ['manage_organization', 'manage_application']

    def get_queryset(self):
        qs = self.selected_organization.members.all()

        if self.q:
            qs = qs.filter(email__istartswith=self.q)

        return qs.order_by('email')


class ApplicationMembersAutocomplete(SelectedApplicationMixin, Select2QuerySetView):
    def get_queryset(self):
        qs = self.selected_application.members.all()

        if self.q:
            qs = qs.filter(Q(name__istartswith=self.q) |
                           Q(friendly_name__istartswith=self.q) |
                           Q(email__istartswith=self.q))

        return qs.order_by('name')


class ApplicationCandidateAutocomplete(SelectedApplicationMixin, Select2QuerySetView):
    def get_queryset(self):
        # returns all organization members not already part of selected application
        qs = self.selected_organization.memberships.exclude(applications__application=self.selected_application)

        if self.q:
            qs = qs.filter(Q(user__name__istartswith=self.q) |
                           Q(user__friendly_name__istartswith=self.q) |
                           Q(user__email__istartswith=self.q))

        return qs.order_by('user__name')
