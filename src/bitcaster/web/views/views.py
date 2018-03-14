from constance import config
from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponseRedirect, HttpResponse
from django.template.loader import get_template
from django.urls import reverse
from django.views.generic import ListView, TemplateView

from bitcaster.db.fields import Role
from bitcaster.models import Subscription

from .base import SelectedApplicationMixin

__all__ = ("IndexView",
           "SubscriptionList", "WorkInProgressView")


class SubscriptionList(SelectedApplicationMixin, ListView):
    model = Subscription

    def get_queryset(self):
        return Subscription.objects.filter(event__application=self.selected_application)


class Error403(TemplateView):
    response_class = HttpResponseForbidden


class WorkInProgressView(TemplateView):
    template_name = 'bitcaster/wip.html'


class PreviewView(TemplateView):
    template_name = 'bitcaster/wip.html'

    def get(self, request, *args, **kwargs):
        tplname = kwargs['path'].replace("|", "/")
        tpl = get_template(tplname)
        content = tpl.render({}, request)
        from premailer import transform
        content = transform(content)
        return HttpResponse(content)

    # def get_template_names(self):
    #     return self.kwargs['path'].replace("|", "/")


class IndexView(TemplateView):
    template_name = 'bitcaster/index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.memberships.filter(role=Role.OWNER):
                url = reverse('org-index', args=[request.user.memberships.first().organization.slug])
                return HttpResponseRedirect(url)
        elif not config.ALLOW_REGISTRATION:
            return HttpResponseRedirect(settings.LOGIN_URL)
        return super().get(request, *args, **kwargs)
