from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import (DetailView, ListView,
                                  )

from mercury.models import Application, Subscription, Organization
from mercury.web.views.base import ApplicationListMixin, SelectedOrganizationMixin


@method_decorator(login_required, name='dispatch')
class OrganizationDetail(ApplicationListMixin, DetailView):
    model = Organization
    slug_url_kwarg = 'org'


@method_decorator(login_required, name='dispatch')
class ApplicationDetail(SelectedOrganizationMixin, DetailView):
    model = Application
    slug_url_kwarg = 'app'


@method_decorator(login_required, name='dispatch')
class SubscriptionList(SelectedOrganizationMixin, ListView):
    model = Subscription

    def get_queryset(self):
        return Subscription.objects.filter(subscriber=self.request.user)
