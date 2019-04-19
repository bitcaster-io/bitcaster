from django.utils.translation import gettext as _
from social_django.models import UserSocialAuth

from ..base import (BitcasterBaseDeleteView, BitcasterTemplateView,
                    HttpResponseRedirectToReferrer,)
from .base import UserMixin


class UserSocialAuthView(UserMixin, BitcasterTemplateView):
    template_name = 'bitcaster/user/social.html'
    title = _('Social login settings')

    def get_context_data(self, **kwargs):
        kwargs['social_auth'] = self.request.user.social_auth.values_list('provider', flat=True)
        return super().get_context_data(**kwargs)


class UserSocialAuthDisconnectView(UserMixin, BitcasterBaseDeleteView):
    template_name = 'bitcaster/user/social.html'
    title = _('Social login settings')
    model = UserSocialAuth

    def get(self, request, *args, **kwargs):
        self.request.user.social_auth.filter(provider=self.kwargs['provider']).delete()
        return HttpResponseRedirectToReferrer(request)
