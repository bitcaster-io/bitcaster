import logging

from django.utils.translation import ugettext as _

from bitcaster.models import OrganizationGroup
from bitcaster.web.forms.organization import OrganizationGroupForm
from bitcaster.web.views.base import (BitcasterBaseCreateView,
                                      BitcasterBaseDeleteView,
                                      BitcasterBaseListView,
                                      BitcasterBaseUpdateView,)

from .org import OrganizationBaseView

logger = logging.getLogger(__name__)


class GroupMixin(OrganizationBaseView):
    model = OrganizationGroup
    form_class = OrganizationGroupForm

    def get_success_url(self):
        return self.selected_organization.urls.groups

    def get_queryset(self):
        return self.selected_organization.groups.all()


class OrganizationGroupCreate(GroupMixin, BitcasterBaseCreateView):
    template_name = 'bitcaster/organization/groups/form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # kwargs.update({'organization': self.selected_organization})
        return kwargs

    def form_valid(self, form):
        form.instance.organization = self.selected_organization
        return super().form_valid(form)


class OrganizationGroupList(GroupMixin, BitcasterBaseListView):
    template_name = 'bitcaster/organization/groups/list.html'
    context_object_name = 'groups'


class OrganizationGroupEdit(GroupMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/organization/groups/form.html'

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return self.selected_organization.groups.get(pk=pk)


class OrganizationGroupDelete(GroupMixin, BitcasterBaseDeleteView):
    message = _('Group <strong>%(object)s</strong> will be removed from %(organization)s')
    user_message = _('Group removed')
