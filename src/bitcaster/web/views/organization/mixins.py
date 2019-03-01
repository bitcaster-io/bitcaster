from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property

from bitcaster.models import Organization, audit_log
from bitcaster.web.views.mixins import SecuredViewMixin


class SelectedOrganizationMixin(SecuredViewMixin):

    def get_context_data(self, **kwargs):
        kwargs['organization'] = self.selected_organization
        return super().get_context_data(**kwargs)

    @cached_property
    def selected_organization(self):  # returns selected office and caches the office
        if 'org' not in self.kwargs:
            return None
        try:
            organization = Organization.objects.get(slug=self.kwargs['org'])
            self.check_perms(self.request, organization, True)
        except Organization.DoesNotExist:
            raise Http404
        return organization

    def audit_log(self, event, **kwargs):
        audit_log(self.request, event,
                  organization=self.selected_organization,
                  **kwargs)


class OrganizationListMixin(SecuredViewMixin):
    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        ret['organizations'] = Organization.objects.filter(members=self.request.user)
        return ret


class ApplicationListMixin(SelectedOrganizationMixin):
    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        if self.selected_organization:
            ret['applications'] = self.selected_organization.applications.all()
        else:
            ret['applications'] = None
        return ret


class OrganizationViewMixin(ApplicationListMixin):
    model = Organization
    slug_url_kwarg = 'org'
    title = '{org}'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/')
        if not request.user.has_perm('org:configure', self.selected_organization):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
