from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from bitcaster import messages
from bitcaster.models import Application
from bitcaster.web.forms import ApplicationCreateForm
from bitcaster.web.views.base import (BitcasterBaseCreateView,
                                      BitcasterBaseListView,)
from bitcaster.web.views.organization.org import OrganizationBaseView


class OrganizationApplications(OrganizationBaseView, BitcasterBaseListView):
    template_name = 'bitcaster/organization/application_list.html'
    success_url = '.'
    model = Application


class ApplicationCreate(OrganizationBaseView, BitcasterBaseCreateView):
    model = Application
    form_class = ApplicationCreateForm
    template_name = 'bitcaster/organization/application_create.html'

    def get_success_url(self):
        return reverse('app-dashboard', args=[self.selected_organization.slug,
                                              self.object.slug])

    def form_valid(self, form):
        form.instance.organization = self.selected_organization
        form.instance.owner = self.request.user
        self.message_user(_('Application created'), messages.SUCCESS)
        return super().form_valid(form)
