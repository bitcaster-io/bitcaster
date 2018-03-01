from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (LoginView as _LoginView,
                                       LogoutView as _LogoutView, )
from django.core.exceptions import PermissionDenied
from django.forms import modelform_factory
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views.generic import (CreateView, DetailView, ListView,
                                  TemplateView, UpdateView, )
from django.views.generic.base import View, ContextMixin
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import ProcessFormView, FormView

from mercury.admin.forms import UserProfileForm, RegistrationForm
from mercury.models import Application, Organization, Subscription, User
from mercury.utils.wsgi import get_client_ip


class LogoutView(_LogoutView):
    next_page = 'login'


class SecuredViewMixin:

    def check_perms(self, request, obj=None, raise_exception=False):
        if not self.permissions:
            return True
        for p in self.permissions:
            if request.user.has_perm(p, obj):
                return True
        if raise_exception:
            raise PermissionDenied('Sorry you have no access to this %s' % obj._meta.verbose_name)
        return False


class SelectedOrganizationMixin:

    @cached_property
    def selected_office(self):  # returns selected office and caches the office
        office = Organization.objects.get(slug=self.kwargs['org'])
        self.check_perms(self.request, office, True)
        return office


class SelectedProjectMixin:

    @cached_property
    def selected_project(self):
        project = self.get_queryset().get(slug=self.kwargs['project'])
        self.check_perms(self.request, project, True)
        return project


@method_decorator(login_required, name='dispatch')
class ApplicationListMixin(View):
    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        ret['applications'] = Application.objects.all()
        return ret


class LoginView(_LoginView):
    template_name = 'bitcaster/login.html'


class MercuryTemplateView(ApplicationListMixin, TemplateView):
    pass


@method_decorator(login_required, name='dispatch')
class ApplicationDetail(ApplicationListMixin, DetailView):
    model = Application


@method_decorator(login_required, name='dispatch')
class SubscriptionList(ApplicationListMixin, ListView):
    model = Subscription

    def get_queryset(self):
        return Subscription.objects.filter(subscriber=self.request.user)


class UserProfile(UpdateView):
    template_name = 'bitcaster/users/profile.html'
    model = User
    form_class = UserProfileForm
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return self.request.user

    # def get_form_class(self):
    #     fields = UserCreationForm._meta.fields
    #     return modelform_factory(User, fields=fields)


class UserRegister(SingleObjectTemplateResponseMixin, FormView):
    template_name = 'bitcaster/users/register.html'
    model = User
    form_class = RegistrationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
