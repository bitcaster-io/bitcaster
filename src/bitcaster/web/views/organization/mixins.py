from django.http import Http404
from django.utils.functional import cached_property

from bitcaster.models import Organization
from bitcaster.web.views.mixins import SecuredViewMixin, SidebarMixin


class SelectedOrganizationMixin(SidebarMixin, SecuredViewMixin):
    permissions = ['manage_organization']

    def get_context_data(self, **kwargs):
        kwargs['organization'] = self.selected_organization
        return super().get_context_data(**kwargs)

    @cached_property
    def selected_organization(self):  # returns selected office and caches the office
        if 'org' not in self.kwargs:
            return None
        try:
            organization = Organization.objects.only('id', 'slug', 'name').get(slug=self.kwargs['org'])
            self.check_perms(self.request, organization, True)
        except Organization.DoesNotExist:
            raise Http404
        return organization


class OrganizationListMixin(SecuredViewMixin):
    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        ret['organizations'] = Organization.objects.filter(members=self.request.user)
        return ret

#
# class ApplicationListMixin(SelectedOrganizationMixin):
#     def get_context_data(self, **kwargs):
#         ret = super().get_context_data(**kwargs)
#         if self.selected_organization:
#             ret['applications'] = self.selected_organization.applications.all()
#         else:
#             ret['applications'] = None
#         return ret
