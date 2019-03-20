from bitcaster.models import ApplicationRole
from bitcaster.web.forms.role import ApplicationRoleForm
from bitcaster.web.views.application.mixins import SelectedApplicationMixin
from bitcaster.web.views.base import (BitcasterBaseCreateView,
                                      BitcasterBaseListView,
                                      BitcasterBaseUpdateView,)


class RoleMixin(SelectedApplicationMixin):
    model = ApplicationRole


class RoleFormMixin(RoleMixin):
    template_name = 'bitcaster/application/roles/form.html'
    form_class = ApplicationRoleForm

    def get_success_url(self):
        return self.selected_application.urls.roles

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'application': self.selected_application})
        return kwargs


class ApplicationRoleList(RoleMixin, BitcasterBaseListView):
    template_name = 'bitcaster/application/roles/list.html'


class ApplicationRoleCreate(RoleFormMixin, BitcasterBaseCreateView):
    pass


class ApplicationRoleUpdate(RoleFormMixin, BitcasterBaseUpdateView):
    pass
