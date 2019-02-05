from django.conf import settings
from django.contrib.messages.storage.fallback import (CookieStorage,
                                                      FallbackStorage,
                                                      SessionStorage,)
from django.utils.deprecation import MiddlewareMixin


class AlarmsCookieStorage(CookieStorage):
    cookie_name = 'alarms'
    not_finished = '__messagesnotfinished__'


class AlarmsSessionStorage(SessionStorage):
    session_key = '_alarms'


class AlarmsFallbackStorage(FallbackStorage):
    storage_classes = (AlarmsCookieStorage, AlarmsSessionStorage)


class MessageMiddleware(MiddlewareMixin):
    """
    Middleware that handles temporary messages.
    """

    def process_request(self, request):
        request._messages = FallbackStorage(request)
        request._alarms = AlarmsFallbackStorage(request)

    def process_response(self, request, response):
        """
        Update the storage backend (i.e., save the messages).

        Raise ValueError if not all messages could be stored and DEBUG is True.
        """
        # A higher middleware layer may return a request which does not contain
        # messages storage, so make no assumption that it will be there.
        if hasattr(request, '_messages'):
            unstored_messages = request._messages.update(response)
            if unstored_messages and settings.DEBUG:
                raise ValueError('Not all temporary messages could be stored.')
        if hasattr(request, '_alarms'):
            unstored_alarms = request._alarms.update(response)
            if unstored_alarms and settings.DEBUG:
                raise ValueError('Not all temporary alarms could be stored.')
        return response
