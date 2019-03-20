from django.http import Http404
from django.utils.functional import cached_property

from bitcaster.models import Application
from bitcaster.state import state
from bitcaster.web.views.organization.mixins import ApplicationListMixin


class SelectedApplicationMixin(ApplicationListMixin):
    def get_context_data(self, **kwargs):
        kwargs['application'] = self.selected_application
        return super().get_context_data(**kwargs)

    @cached_property
    def selected_application(self):
        if self.selected_organization and 'app' in self.kwargs:
            slug = self.kwargs['app']
            try:
                app = self.selected_organization.applications.get(slug=slug)
                state.debug['application'] = app
                self.check_perms(self.request, app, True)
            except Application.DoesNotExist:  # pragma: no cover
                raise Http404
            return app
        return None
