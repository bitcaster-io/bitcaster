import logging

from django.forms import inlineformset_factory
from django.utils.translation import ugettext as _
from django.views.generic.edit import FormMixin, ModelFormMixin, ProcessFormView

from bitcaster.models import Application, ApplicationMember
from bitcaster.web.forms import ApplicationMemberForm
from bitcaster.web.forms.applicationmember import ApplicationMemberFormSet
from bitcaster.web.views.application.app import ApplicationViewMixin
from bitcaster.web.views.base import (BitcasterBaseCreateView,
                                      BitcasterBaseDeleteView,
                                      BitcasterBaseUpdateView, TemplateView,)
from bitcaster.web.views.mixins import TitleMixin

logger = logging.getLogger(__name__)


class MemberMixin(ApplicationViewMixin):
    model = ApplicationMember

    def get_success_url(self):
        return self.selected_application.urls.members

    def get_queryset(self):
        return self.selected_application.memberships.all()


class MemberFormMixin(ModelFormMixin):
    # form_class = ApplicationMemberFormSet
    # def get_form(self, form_class=None):
    #     form = super().get_form(form_class)
    #     form.helper = FormHelper(form)
    #     form.helper.form_show_labels = False
    #     return form

    def form_valid(self, form):
        form.instance.application = self.selected_application
        return super().form_valid(form)


class ApplicationMembershipList(MemberMixin, TitleMixin, FormMixin, ProcessFormView, TemplateView):
    template_name = 'bitcaster/application/members/list.html'
    # form_class = ApplicationMemberFormSet
    title = _('Application members')

    def get_form_class(self):
        return inlineformset_factory(Application,
                                     ApplicationMember,
                                     form=ApplicationMemberForm,
                                     min_num=0,
                                     labels={'role': '', 'org_member': ''},
                                     extra=0)

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super(ApplicationMembershipList, self).get_form_kwargs()
        kwargs['instance'] = self.selected_application
        return kwargs

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        ret['formset'] = ret['form']
        return ret

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ApplicationMembershipCreate(MemberMixin, MemberFormMixin, BitcasterBaseCreateView):
    template_name = 'bitcaster/application/members/add.html'
    form_class = ApplicationMemberFormSet
    title = _('Add member')

    def get_form_kwargs(self):
        ret = super().get_form_kwargs()
        ret['application'] = self.selected_application
        return ret

    def form_valid(self, formset):
        formset.instance = self.selected_application
        formset.save()
        return super().form_valid(formset)


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
