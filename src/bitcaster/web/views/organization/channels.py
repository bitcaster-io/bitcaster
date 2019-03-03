from django.utils.translation import gettext_lazy as _

from bitcaster.web.views.channel import (ChannelCreateWizard, ChannelDeleteView,
                                         ChannelDeprecateView, ChannelListView,
                                         ChannelTestView, ChannelToggleView,
                                         ChannelUpdateView, ChannelUsageView,)

from .mixins import OrganizationViewMixin


class ChannelMixin(OrganizationViewMixin):

    def get_queryset(self):
        return self.selected_organization.channels.valid()

    def get_success_url(self):
        return self.selected_organization.urls.channels

    def get_redirect_url(self, *args, **kwargs):
        return self.selected_organization.urls.channels


class OrganizationChannels(ChannelMixin, OrganizationViewMixin, ChannelListView):
    template_name = 'bitcaster/organization/channels/list.html'
    title = _('Channels')


class OrganizationChannelUpdate(ChannelMixin, ChannelUpdateView):
    template_name = 'bitcaster/organization/channels/configure.html'
    title = _('Edit Channel')


class OrganizationChannelRemove(ChannelMixin, ChannelDeleteView):
    pass


class OrganizationChannelToggle(ChannelMixin, ChannelToggleView):
    pass


class OrganizationChannelUsage(ChannelMixin, ChannelUsageView):
    template_name = 'bitcaster/organization/channels/usage.html'


class OrganizationChannelTest(ChannelMixin, ChannelTestView):
    pass


class OrganizationChannelDeprecate(ChannelMixin, ChannelDeprecateView):
    pass


class OrganizationChannelCreate(ChannelMixin, ChannelCreateWizard):
    TEMPLATES = {'a': 'bitcaster/organization/channels/create_wizard_1.html',
                 'b': 'bitcaster/organization/channels/create_wizard_2.html',
                 }

    def get_extra_instance_kwargs(self):
        return super().get_extra_instance_kwargs(organization=self.selected_organization)
