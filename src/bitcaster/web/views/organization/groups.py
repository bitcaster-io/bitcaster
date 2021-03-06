import logging

from django.forms import modelform_factory
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from django.views.generic.edit import ModelFormMixin
from sentry_sdk import capture_exception

from bitcaster.models import OrganizationGroup
from bitcaster.utils.http import get_query_string
from bitcaster.web.forms import OrganizationGroupForm
from bitcaster.web.forms.organizationgroup import OrganizationGroupAddMemberForm
from bitcaster.web.views.base import (BitcasterBaseCreateView,
                                      BitcasterBaseDeleteView,
                                      BitcasterBaseListView,
                                      BitcasterBaseUpdateView,)

from .org import OrganizationBaseView

logger = logging.getLogger(__name__)


class GroupMixin(OrganizationBaseView):
    model = OrganizationGroup

    def get_queryset(self):
        return self.selected_organization.groups.all()


class SelectedGroupMixin(GroupMixin):
    model = OrganizationGroup
    pk_url_kwarg = 'group'

    @cached_property
    def selected_group(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return self.selected_organization.groups.get(pk=pk)

    def get_context_data(self, **kwargs):
        return super().get_context_data(group=self.selected_group, **kwargs)


class OrganizationGroupFormMixin(ModelFormMixin):
    form_class = OrganizationGroupForm
    form_show_labels = True

    def form_valid(self, form):
        form.instance.organization = self.selected_organization
        return super().form_valid(form)

    def get_form_class(self):
        return modelform_factory(OrganizationGroup, form=OrganizationGroupForm,
                                 fields=self.fields)

    def get_success_url(self):
        return reverse('org-group-settings', args=[self.selected_organization.slug,
                                                   self.object.pk])


class OrganizationGroupList(GroupMixin, BitcasterBaseListView):
    template_name = 'bitcaster/organization/groups/list.html'
    context_object_name = 'groups'


class OrganizationGroupCreate(GroupMixin, OrganizationGroupFormMixin, BitcasterBaseCreateView):
    template_name = 'bitcaster/organization/groups/create.html'
    fields = ('name', 'closed')

    def form_valid(self, form):
        return super().form_valid(form)


class OrganizationGroupEdit(SelectedGroupMixin, OrganizationGroupFormMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/organization/groups/edit.html'

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return self.selected_organization.groups.get(pk=pk)

    def get_success_url(self):
        return reverse('org-groups', args=[self.selected_organization.slug])


class OrganizationGroupMembers(SelectedGroupMixin, BitcasterBaseListView):
    title = _('%(name)s members')
    template_name = 'bitcaster/organization/groups/members.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(form=OrganizationGroupAddMemberForm(),
                                        name=self.selected_group.name,
                                        filters=get_query_string(self.request, remove=['page']),
                                        member_automplete_url=reverse('org-member-autocomplete',
                                                                      args=[
                                                                          self.selected_organization.slug,
                                                                      ]),
                                        **kwargs)

    def post(self, request, *args, **kwargs):
        form = OrganizationGroupAddMemberForm(data=request.POST)
        if form.is_valid():
            try:
                pk = form.cleaned_data['user']
                user = self.selected_organization.memberships.get(user__id=pk)
                self.selected_group.members.add(user)
            except Exception as e:
                capture_exception(e)

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = self.selected_group.members.all()
        target = self.request.GET.get('filter')
        if target:
            qs = qs.filter(user__friendly_name__istartswith=target)
        return qs.order_by('user__email')


class OrganizationGroupApplications(SelectedGroupMixin, BitcasterBaseListView):
    template_name = 'bitcaster/organization/groups/applications.html'

    def get_queryset(self):
        return self.selected_group.applications.all()


class OrganizationGroupDelete(GroupMixin, BitcasterBaseDeleteView):
    message = _('Group <strong>%(object)s</strong> will be removed from %(organization)s')
    user_message = _('Group removed')
    pk_url_kwarg = 'group'

    def get_success_url(self):
        return reverse('org-groups', args=[self.selected_organization.slug])


class OrganizationGroupMemberRemove(SelectedGroupMixin, BitcasterBaseDeleteView):
    message = _('User <strong>%(object)s</strong> will be removed from group')
    user_message = _('User removed')
    title = _('Remove user from group')

    def get_object(self, queryset=None):
        return self.selected_group.members.get(pk=self.kwargs.get('member'))

    def get_success_url(self):
        return reverse('org-group-members', args=[self.selected_organization.slug,
                                                  self.selected_group.pk
                                                  ])
