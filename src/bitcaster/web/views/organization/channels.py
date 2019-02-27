from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from bitcaster.web.views.channel import (ChannelCreateWizard, ChannelDeleteView,
                                         ChannelDeprecateView, ChannelTestView,
                                         ChannelToggleView, ChannelUpdateView,
                                         ChannelUsageView,)

from .mixins import (ApplicationListMixin, OrganizationAuditMixin,
                     OrganizationViewMixin,)


class OrganizationChannels(OrganizationAuditMixin, ApplicationListMixin, ListView):
    template_name = 'bitcaster/organization/channels/list.html'

    def get_queryset(self):
        return self.selected_organization.channels.valid()

    def get_context_data(self, **kwargs):
        kwargs['channel_context'] = self.selected_organization
        kwargs['title'] = _('Organization Channels')
        kwargs['create_url'] = reverse('org-channel-create',
                                       args=[self.selected_organization.slug])
        return super().get_context_data(**kwargs)


class OrganizationChannelUpdate(OrganizationViewMixin, ChannelUpdateView):
    template_name = 'bitcaster/organization/channels/configure.html'

    def get_success_url(self):
        return reverse_lazy('org-channel-list',
                            args=[self.selected_organization.slug])

    def get_queryset(self):
        return self.selected_organization.channels.all()


class OrganizationChannelRemove(OrganizationViewMixin, ChannelDeleteView):
    template_name = 'bitcaster/organization/channels/remove.html'

    def get_success_url(self):
        return reverse_lazy('org-channel-list',
                            args=[self.selected_organization.slug])

    def get_queryset(self):
        return self.selected_organization.channels.all()


class OrganizationChannelToggle(OrganizationViewMixin, ChannelToggleView):
    pattern_name = 'org-channel-list'

    def get_queryset(self):
        return self.selected_organization.channels.all()

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('org-channel-list',
                            args=[self.selected_organization.slug])


class OrganizationChannelUsage(OrganizationViewMixin, ChannelUsageView):
    template_name = 'bitcaster/organization/channels/usage.html'
    pattern_name = 'org-channel-usage'

    def get_queryset(self):
        return self.selected_organization.channels.all()


class OrganizationChannelTest(OrganizationViewMixin, ChannelTestView):
    pattern_name = 'org-channel-test'

    def get_queryset(self):
        return self.selected_organization.channels.all()

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('org-channel-list',
                            args=[self.selected_organization.slug])


class OrganizationChannelDeprecate(OrganizationViewMixin, ChannelDeprecateView):
    pattern_name = 'org-channel-list'

    def get_queryset(self):
        return self.selected_organization.channels.all()

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('org-channel-list',
                            args=[self.selected_organization.slug])


class OrganizationChannelCreate(OrganizationViewMixin, ChannelCreateWizard):
    TEMPLATES = {'a': 'bitcaster/organization/channels/create_wizard_1.html',
                 'b': 'bitcaster/organization/channels/create_wizard_2.html',
                 }

    def get_success_url(self):
        return reverse_lazy('org-channel-list', args=[self.selected_organization.slug])

    def get_extra_instance_kwargs(self):
        return {'organization': self.selected_organization}
