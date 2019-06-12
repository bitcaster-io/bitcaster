from django.http import HttpResponseRedirect
from django.urls import reverse
from social_core.exceptions import AuthCanceled, AuthFailed

from bitcaster.exceptions import NotMemberOfOrganization
from bitcaster.web.messages import alarms


class ExceptionHandlerMiddleware:
    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        # Actually this code is only used if DEBUG=True
        # and it is needed to provide the same behaviour as in production (DEBUG=False)
        if isinstance(exception, (NotMemberOfOrganization, AuthFailed, AuthCanceled)):
            alarms.error(request, str(exception))
            url = reverse('login')
            return HttpResponseRedirect(url)
