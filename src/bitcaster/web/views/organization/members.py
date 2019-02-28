import logging

from django.urls import reverse
from django.utils.translation import ugettext as _

from bitcaster.models import OrganizationMember
from bitcaster.web.views.base import (BitcasterBaseDeleteView,
                                      BitcasterBaseListView,
                                      BitcasterBaseUpdateView,)
from bitcaster.web.views.organization.mixins import OrganizationViewMixin

logger = logging.getLogger(__name__)


class OrganizationMembershipList(OrganizationViewMixin, BitcasterBaseListView):
    template_name = 'bitcaster/organization/members/list.html'
    success_url = '.'
    model = OrganizationMember

    def get_context_data(self, **kwargs):
        data = super(OrganizationMembershipList, self).get_context_data(**kwargs)
        # data['memberships'] = OrganizationMember.objects.filter(user__isnull=False)
        # data['invitations'] = OrganizationMember.objects.filter(user__isnull=True)
        base = self.selected_organization.memberships.exclude(user=self.selected_organization.owner)
        data['memberships'] = base.filter(user__isnull=False)
        data['invitations'] = base.filter(user__isnull=True)
        return data


class OrganizationMembershipEdit(OrganizationViewMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/organization/members/edit.html'
    fields = ('role',)
    success_url = ''
    model = OrganizationMember

    def get_template_names(self):
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        kwargs['title'] = _('Edit Membership')
        kwargs['membership'] = self.object
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        self.message_user(_('Updated'))
        return super(OrganizationMembershipEdit, self).form_valid(form)

    def get_success_url(self):
        return reverse('org-members', args=[self.selected_organization.slug])


class OrganizationMembershipDelete(OrganizationViewMixin, BitcasterBaseDeleteView):

    def get_success_url(self):
        return reverse('org-members', args=[self.selected_organization.slug])

    def get_queryset(self):
        return self.selected_organization.memberships.filter(user__isnull=False)

    def delete(self, request, *args, **kwargs):
        ret = super().delete(request, *args, **kwargs)
        self.message_user('Membership removed')
        return ret
