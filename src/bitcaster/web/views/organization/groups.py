import logging

from django.forms import modelform_factory
from django.utils.translation import ugettext as _
from django.views.generic.edit import ModelFormMixin

from bitcaster.models import OrganizationGroup
from bitcaster.web.forms import OrganizationGroupForm
from bitcaster.web.views.base import (BitcasterBaseCreateView,
                                      BitcasterBaseDeleteView,
                                      BitcasterBaseListView,
                                      BitcasterBaseUpdateView,)

from .org import OrganizationBaseView

logger = logging.getLogger(__name__)


class GroupMixin(OrganizationBaseView):
    model = OrganizationGroup

    def get_success_url(self):
        return self.selected_organization.urls.groups

    def get_queryset(self):
        return self.selected_organization.groups.all()


class OrganizationGroupFormMixin(ModelFormMixin):
    form_class = OrganizationGroupForm
    form_show_labels = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'organization': self.selected_organization,
                       'form_show_labels': self.form_show_labels})
        return kwargs

    def form_valid(self, form):
        form.instance.organization = self.selected_organization
        return super().form_valid(form)

    def get_form_class(self):
        return modelform_factory(OrganizationGroup, form=OrganizationGroupForm,
                                 fields=self.fields)


class OrganizationGroupList(GroupMixin, BitcasterBaseListView):
    template_name = 'bitcaster/organization/groups/list.html'
    context_object_name = 'groups'


class OrganizationGroupCreate(GroupMixin, OrganizationGroupFormMixin, BitcasterBaseCreateView):
    template_name = 'bitcaster/organization/groups/form.html'
    fields = ('name', 'closed')


class OrganizationGroupEdit(GroupMixin, OrganizationGroupFormMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/organization/groups/form.html'
    fields = ('name', 'closed',)

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return self.selected_organization.groups.get(pk=pk)


class OrganizationGroupMembers(OrganizationGroupEdit):
    fields = ('members',)
    form_show_labels = False


class OrganizationGroupApplications(OrganizationGroupEdit):
    fields = ('applications',)
    form_show_labels = False


class OrganizationGroupDelete(GroupMixin, BitcasterBaseDeleteView):
    message = _('Group <strong>%(object)s</strong> will be removed from %(organization)s')
    user_message = _('Group removed')
