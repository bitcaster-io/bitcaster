import logging

from crispy_forms.helper import FormHelper
from django.utils.translation import ugettext as _

from bitcaster.models import OrganizationMember
from bitcaster.web.views.base import (BitcasterBaseDeleteView,
                                      BitcasterBaseListView,
                                      BitcasterBaseUpdateView,)

from .org import OrganizationBaseView

logger = logging.getLogger(__name__)


class MemberMixin(OrganizationBaseView):
    model = OrganizationMember

    def get_success_url(self):
        return self.selected_organization.urls.members

    def get_queryset(self):
        return self.selected_organization.memberships.exclude(user=self.selected_organization.owner)


class OrganizationMembershipList(MemberMixin, BitcasterBaseListView):
    template_name = 'bitcaster/organization/members/list.html'

    # title = _('Users')

    def get_context_data(self, **kwargs):
        data = super(OrganizationMembershipList, self).get_context_data(**kwargs)
        base = self.get_queryset()
        data['memberships'] = base.filter(user__isnull=False)
        data['invitations'] = base.filter(user__isnull=True)
        return data


class OrganizationMembershipEdit(MemberMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/organization/members/form.html'
    fields = ('role',)
    # title = _('Edit Membership')
    context_object_name = 'membership'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper(form)
        form.helper.form_show_labels = False
        return form

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return self.selected_organization.memberships.get(pk=pk)


class OrganizationMembershipDelete(MemberMixin, BitcasterBaseDeleteView):
    message = _('User <strong>%(object)s</strong> will be removed from %(organization)s')
    user_message = _('User removed')
