from django.http import (Http404, HttpResponse, HttpResponseForbidden,
                         HttpResponseRedirect,)
from django.template.loader import get_template
from django.urls import reverse
from django.views.generic import RedirectView, TemplateView

__all__ = ('IndexView', 'WorkInProgressView')


class Error403(TemplateView):
    response_class = HttpResponseForbidden


class WorkInProgressView(TemplateView):
    template_name = 'bitcaster/wip.html'


class PreviewView(TemplateView):
    template_name = 'bitcaster/wip.html'

    def get(self, request, *args, **kwargs):
        tplname = kwargs['path'].replace('|', '/')
        tpl = get_template(tplname)
        content = tpl.render({}, request)
        from premailer import transform
        content = transform(content)
        return HttpResponse(content)

    # def get_template_names(self):
    #     return self.kwargs['path'].replace("|", "/")


class IndexView(RedirectView):
    url = '/login/'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            membership = request.user.memberships.first()
            if membership:
                return HttpResponseRedirect(reverse('me', args=[membership.organization.slug]))
            else:
                raise Http404('%s: No membership' % request.user.email)
        return super().get(request, *args, **kwargs)
        #     elif self.request.user.is_superuser:
        #         pass
        #     # if request.user.memberships.filter(role=ROLES.OWNER):
        #     #     url = reverse('org-dashboard', args=[request.user.memberships.first().organization.slug])
        #     #     return HttpResponseRedirect(url)
        #     # elif request.user.memberships.filter(role=ROLES.MEMBER):
        #     #     url = reverse('user-org', args=[request.user.memberships.first().organization.slug])
        #     #     return HttpResponseRedirect(url)
        #
        # elif not config.ALLOW_REGISTRATION:
        #     return HttpResponseRedirect(settings.LOGIN_URL)
        # return super().get(request, *args, **kwargs)
