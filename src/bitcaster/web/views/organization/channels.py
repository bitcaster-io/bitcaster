from django.utils.translation import gettext_lazy as _

from bitcaster.models import Channel
from bitcaster.web.views.channel import (ChannelCreateWizard, ChannelDeleteView,
                                         ChannelDeprecateView, ChannelListView,
                                         ChannelTestView, ChannelToggleView,
                                         ChannelUpdateView, ChannelUsageView,)

from .org import OrganizationBaseView


class ChannelMixin(OrganizationBaseView):
    model = Channel

    def get_queryset(self):
        return self.selected_organization.channels.valid()

    def get_success_url(self):
        return self.selected_organization.urls.channels

    def get_redirect_url(self, *args, **kwargs):
        return self.selected_organization.urls.channels


class OrganizationChannels(ChannelMixin, ChannelListView):
    template_name = 'bitcaster/organization/channel/list.html'


class OrganizationChannelUpdate(ChannelMixin, ChannelUpdateView):
    template_name = 'bitcaster/organization/channel/form.html'
    permissions = ['edit_channel']


class OrganizationChannelRemove(ChannelMixin, ChannelDeleteView):
    pass


class OrganizationChannelToggle(ChannelMixin, ChannelToggleView):
    pass


class OrganizationChannelUsage(ChannelMixin, ChannelUsageView):
    template_name = 'bitcaster/organization/channel/_info.html'


class OrganizationChannelTest(ChannelMixin, ChannelTestView):
    pass


class OrganizationChannelDeprecate(ChannelMixin, ChannelDeprecateView):
    pass


class OrganizationChannelCreate(ChannelMixin, ChannelCreateWizard):
    TEMPLATES = {'a': 'bitcaster/organization/channel/create_wizard_1.html',
                 'b': 'bitcaster/organization/channel/create_wizard_2.html',
                 }
    title = _('Create Channel')
    permissions = ['create_channel']

    def check_perms(self, request, obj=None, raise_exception=False):
        return super().check_perms(request, obj, raise_exception)

    def get_extra_instance_kwargs(self):
        return super().get_extra_instance_kwargs(organization=self.selected_organization)
