from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (LoginView as _LoginView,
                                       LogoutView as _LogoutView,)
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, TemplateView

from mercury.models import Application, Subscription


class LogoutView(_LogoutView):
    next_page = 'login'


class ApplicationListMixin:
    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        ret['applications'] = Application.objects.all()
        return ret


class LoginView(_LoginView):
    template_name = 'bitcaster/login.html'


class HomeView(ApplicationListMixin, TemplateView):
    template_name = 'bitcaster/index.html'


@method_decorator(login_required, name='dispatch')
class ApplicationDetail(ApplicationListMixin, DetailView):
    model = Application


@method_decorator(login_required, name='dispatch')
class SubscriptionList(ApplicationListMixin, ListView):
    model = Subscription

    def get_queryset(self):
        return Subscription.objects.filter(subscriber=self.request.user)
