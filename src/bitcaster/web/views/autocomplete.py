from dal_select2.views import Select2QuerySetView

from bitcaster.models import Channel, OrganizationMember
from bitcaster.web.views.organization.mixins import SelectedOrganizationMixin


class UserAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return OrganizationMember.objects.none()

        qs = OrganizationMember.objects.all()

        if self.q:
            qs = qs.filter(email__istartswith=self.q)

        return qs


class ChannelAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Channel.objects.none()

        qs = Channel.objects.all()

        if self.q:
            qs = qs.filter(email__istartswith=self.q)

        return qs


class AddressAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        qs = self.request.user.addresses.all()

        if self.q:
            qs = qs.filter(address__istartswith=self.q)

        return qs


class ApplicationAutocomplete(SelectedOrganizationMixin, Select2QuerySetView):
    def get_queryset(self):
        qs = self.selected_organization.applications.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class OrganizationMembersAutocomplete(SelectedOrganizationMixin, Select2QuerySetView):
    def get_queryset(self):
        qs = self.selected_organization.members.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs
