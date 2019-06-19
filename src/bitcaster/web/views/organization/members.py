import logging

from constance import config
from crispy_forms.helper import FormHelper
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic.edit import ModelFormMixin

from bitcaster.models import OrganizationMember
from bitcaster.utils.http import get_query_string
from bitcaster.web.forms import OrganizationMemberForm
from bitcaster.web.views.base import (BitcasterBaseDeleteView,
                                      BitcasterBaseListView,
                                      BitcasterBaseUpdateView,)
from bitcaster.web.views.mixins import FilterQuerysetMixin

from .org import OrganizationBaseView

logger = logging.getLogger(__name__)


class MemberMixin(OrganizationBaseView):
    model = OrganizationMember

    def get_success_url(self):
        return self.selected_organization.urls.members

    def get_queryset(self):
        return self.selected_organization.memberships.exclude(user=self.selected_organization.owner)


class MemberFormMixin(ModelFormMixin):
    form_class = OrganizationMemberForm
    form_show_labels = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'organization': self.selected_organization,
                       'user_role': self.request.user.memberships.get(organization=self.selected_organization).role,
                       'form_show_labels': self.form_show_labels})
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper(form)
        form.helper.form_show_labels = False
        return form

    def form_valid(self, form):
        form.instance.organization = self.selected_organization
        return super().form_valid(form)


class OrganizationMembershipList(MemberMixin, FilterQuerysetMixin, BitcasterBaseListView):
    template_name = 'bitcaster/organization/members/list.html'
    search_fields = ['user__name__istartswith']
    filter_fieldmap = {
        # Translators: UserNotificationLogView.filter_fieldmap
        _('email'): 'user__email',
    }

    def get_queryset(self):
        qs = self.selected_organization.memberships.exclude(user=self.selected_organization.owner)
        qs = qs.select_related('user')
        qs = self.filter_queryset(qs)
        return qs.order_by('user__email')

    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     target = self.request.GET.get('filter')
    #     if target:
    #         qs = qs.filter(user__email__istartswith=target)
    #     return qs.order_by('user__email')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['ENABLE_IMPERSONATE'] = config.ENABLE_IMPERSONATE
        data['filters'] = get_query_string(self.request, remove=['page'])
        data['user_role'] = self.request.user.memberships.get(organization=self.selected_organization).role
        data['memberships'] = self.get_queryset()
        data['invitations'] = self.selected_organization.invitations.filter(date_accepted=None)
        return data


class OrganizationMembershipEdit(MemberMixin, MemberFormMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/organization/members/form.html'
    context_object_name = 'membership'

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return self.selected_organization.memberships.get(pk=pk)


class OrganizationMembershipDelete(MemberMixin, BitcasterBaseDeleteView):
    message = _('User <strong>%(object)s</strong> will be removed from %(organization)s')
    user_message = _('User removed')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.user.delete()
        return HttpResponseRedirect(success_url)
