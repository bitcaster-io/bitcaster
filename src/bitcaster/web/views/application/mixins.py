from django.http import Http404
from django.utils.functional import cached_property

from bitcaster.models import Application
from bitcaster.state import state
from bitcaster.web.views.organization.mixins import SelectedOrganizationMixin


class SelectedApplicationMixin(SelectedOrganizationMixin):
    permissions = ['manage_application']

    def get_context_data(self, **kwargs):
        kwargs['application'] = self.selected_application
        return super().get_context_data(**kwargs)

    @cached_property
    def selected_organization(self):  # returns selected office and caches the office
        return self.selected_application.organization

    @cached_property
    def selected_application(self):
        if 'app' in self.kwargs:
            slug = self.kwargs['app']
            try:
                app = Application.objects.filter(slug=slug,
                                                 organization__slug=self.kwargs['org']).first()
                state.debug['application'] = app
                self.check_perms(self.request, app, True)
            except Application.DoesNotExist:  # pragma: no cover
                raise Http404
            return app
        return None
