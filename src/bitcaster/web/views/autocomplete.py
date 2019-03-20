from dal_select2.views import Select2QuerySetView

from bitcaster.models import Address, Channel, OrganizationMember


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
        return Address.objects.all()

        if not self.request.user.is_authenticated:
            return Address.objects.all()

        qs = self.request.user.addresses.all()

        # if self.q:
        #     qs = qs.filter(address__istartswith=self.q)

        return qs
