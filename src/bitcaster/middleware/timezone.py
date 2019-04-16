from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


class UserTimezoneMiddleware(MiddlewareMixin):

    def process_request(self, request):
        try:
            timezone.activate(request.user.timezone)
        except Exception:
            pass
        return None
