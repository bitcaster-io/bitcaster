from django.utils import translation

from bitcaster.config import settings
from bitcaster.utils.language import get_attr


class UserLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user and request.user.is_authenticated:
            translation.activate(request.user.language)

        response = self.get_response(request)
        # FIXME: here user can be Application due TriggerKeyAuthentication
        if get_attr(request, 'user.is_authenticated') and request.user.is_authenticated:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, request.user.language)
        return response
