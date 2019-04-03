from django.http import HttpResponseRedirect

from bitcaster.exceptions import NotMemberOfOrganization
from bitcaster.messages import alarms


class RedirectToRefererResponse(HttpResponseRedirect):
    def __init__(self, request, *args, **kwargs):
        redirect_to = request.META.get('HTTP_REFERER', '/')
        super().__init__(
            redirect_to, *args, **kwargs)


class ExceptionHandlerMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, NotMemberOfOrganization):
            message = 'Sorry, you do not seem to be a public member of %s' % exception.backend.setting('NAME')
            alarms.error(request, message)
            return RedirectToRefererResponse(request)
