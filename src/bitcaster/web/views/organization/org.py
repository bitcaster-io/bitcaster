import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView

from bitcaster.models import Organization
from bitcaster.web.forms import OrganizationForm
from bitcaster.web.forms.organization import OrganizationOptionsForm
from bitcaster.web.views.mixins import TitleMixin
from bitcaster.web.views.organization.mixins import SelectedOrganizationMixin

from ..base import BitcasterBaseDetailView, BitcasterBaseUpdateView

logger = logging.getLogger(__name__)


class OrganizationBaseView(TitleMixin, SelectedOrganizationMixin):
    model = Organization
    slug_url_kwarg = 'org'
    target = 'selected_organization'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/')
        if not request.user.has_perm('manage_organization', self.selected_organization):
            raise PermissionDenied("'admin' permission needed")
        return super().dispatch(request, *args, **kwargs)


class OrganizationDashboard(OrganizationBaseView, BitcasterBaseDetailView):
    template_name = 'bitcaster/organization/dashboard.html'

    @property
    def title(self):
        return self.selected_organization.name

    def get_context_data(self, **kwargs):
        kwargs['occurences'] = self.selected_organization.occurences.active()
        kwargs['locks'] = self.selected_organization.occurences.active(processing__isnull=False)
        return super().get_context_data(**kwargs)


class OrganizationConfiguration(OrganizationBaseView, BitcasterBaseUpdateView):
    form_class = OrganizationForm
    success_url = '.'
    template_name = 'bitcaster/organization/form.html'

    def form_valid(self, form):
        slug = form.cleaned_data.get('slug', None)
        self.object = form.save()
        url = reverse('org-config', args=[slug or self.object.slug])
        self.message_user(_('Configuration saved'), messages.SUCCESS)
        return HttpResponseRedirect(url)


class OrganizationCheckConfigView(OrganizationBaseView, RedirectView):
    pattern_name = 'org-dashboard'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class OrganizationOptionsView(OrganizationBaseView, BitcasterBaseUpdateView):
    form_class = OrganizationOptionsForm
    success_url = '.'
    template_name = 'bitcaster/organization/options.html'

    # def form_valid(self, form):
    #     slug = form.cleaned_data.get('slug', None)
    #     self.object = form.save()
    #     url = reverse('org-config', args=[slug or self.object.slug])
    #     self.message_user(_('Configuration saved'), messages.SUCCESS)
    #     return HttpResponseRedirect(url)

    # def get_form(self, form_class=None):
    #     form_class = self.get_form_class()
    #     kwargs = self.get_form_kwargs()
    #     for f in form_class.declared_fields.keys():
    #         value = getattr(config, f, '')
    #         if isinstance(value, dict):
    #             value = str(value)
    #         kwargs['initial'][f] = value
    #     return form_class(**kwargs)

    # def form_valid(self, form):
    #     for k, v in form.cleaned_data.items():
    #         # TODO: remove me
    #         print(111, "org.py:96", 111111, k, v)
    #     #     setattr(config, k, v)
    #     # self.message_user(_('Configuration saved'), messages.SUCCESS)
    #     # if self.bit:
    #     #     config.SYSTEM_CONFIGURED |= self.bit
    #     return super().form_valid(form)
