import logging

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.views.generic.edit import ModelFormMixin

from bitcaster.models import ApplicationMember
from bitcaster.utils.http import get_query_string
from bitcaster.web.forms import ApplicationMemberForm
from bitcaster.web.forms.applicationmember import ApplicationMemberAddForm
from bitcaster.web.views.application.app import ApplicationViewMixin
from bitcaster.web.views.base import (BitcasterBaseCreateView,
                                      BitcasterBaseDeleteView,
                                      BitcasterBaseListView,
                                      BitcasterBaseUpdateView,)

logger = logging.getLogger(__name__)


class MemberMixin(ApplicationViewMixin):
    model = ApplicationMember

    def get_success_url(self):
        return self.selected_application.urls.members

    def get_queryset(self):
        return self.selected_application.memberships.all()


class MemberFormMixin(ModelFormMixin):
    form_class = ApplicationMemberForm

    def get_context_data(self, **kwargs):
        kwargs['members_autocomplete_url'] = reverse('app-candidate-autocomplete',
                                                     args=[self.selected_organization.slug,
                                                           self.selected_application.slug,
                                                           ])
        return super().get_context_data(**kwargs)


class ApplicationMembershipList(MemberMixin, BitcasterBaseListView):
    template_name = 'bitcaster/application/members/list.html'
    title = _('Application members')

    def get_queryset(self):
        qs = super().get_queryset()
        target = self.request.GET.get('filter')
        if target:
            qs = qs.filter(org_member__user__email__istartswith=target)
        return qs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['filters'] = get_query_string(self.request, remove=['page'])
        return data


# class ApplicationMembershipList(MemberMixin, TitleMixin, FormMixin, ProcessFormView, TemplateView):
#     template_name = 'bitcaster/application/members/list.html'
#     # form_class = ApplicationMemberFormSet
#     title = _('Application members')
#
#     def get_form_class(self):
#         return inlineformset_factory(Application,
#                                      ApplicationMember,
#                                      form=ApplicationMemberForm,
#                                      min_num=0,
#                                      labels={'role': '', 'org_member': ''},
#                                      extra=0)
#
#     def get_form_kwargs(self):
#         """Return the keyword arguments for instantiating the form."""
#         kwargs = super().get_form_kwargs()
#         kwargs['instance'] = self.selected_application
#         return kwargs
#
#     def post(self, request, *args, **kwargs):
#         return super().post(request, *args, **kwargs)
#
#     def get_context_data(self, **kwargs):
#         ret = super().get_context_data(**kwargs)
#         ret['formset'] = ret['form']
#         return ret
#
#     def form_valid(self, form):
#         form.save()
#         return super().form_valid(form)


class ApplicationMembershipCreate(MemberMixin, MemberFormMixin, BitcasterBaseCreateView):
    template_name = 'bitcaster/application/members/add.html'
    form_class = ApplicationMemberAddForm
    title = _('Add members')

    def get_form_kwargs(self):
        ret = super().get_form_kwargs()
        ret['application'] = self.selected_application
        return ret

    def form_valid(self, form):
        role = form.cleaned_data['role']
        self.selected_application.add_member(form.cleaned_data['members'],
                                             role)
        return HttpResponseRedirect(self.get_success_url())


class ApplicationMembershipEdit(MemberMixin, MemberFormMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/application/members/form.html'
    context_object_name = 'membership'

    def form_valid(self, form):
        form.instance.org_member = self.get_object().org_member
        form.instance.application = self.selected_application
        form.save()
        return super().form_valid(form)

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return self.selected_application.memberships.get(pk=pk)


class ApplicationMembershipDelete(MemberMixin, BitcasterBaseDeleteView):
    message = _('User <strong>%(object)s</strong> will be removed from %(application)s')
    user_message = _('User removed')
    template_name = 'bitcaster/application/confirm_delete.html'
