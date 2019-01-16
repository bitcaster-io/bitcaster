from django.contrib.messages import MessageFailure

DEBUG = 10
INFO = 20
SUCCESS = 25
WARNING = 30
ERROR = 40

DEFAULT_TAGS = {
    DEBUG: 'debug',
    INFO: 'info',
    SUCCESS: 'success',
    WARNING: 'warning',
    ERROR: 'error'
}

DEFAULT_LEVELS = {
    'DEBUG': DEBUG,
    'INFO': INFO,
    'SUCCESS': SUCCESS,
    'WARNING': WARNING,
    'ERROR': ERROR
}


def add_message(request, level, message, extra_tags='', fail_silently=False):
    """
    Attempt to add a message to the request using the 'messages' app.
    """
    try:
        messages = request._messages
    except AttributeError:
        if not hasattr(request, 'META'):
            raise TypeError(
                'add_message() argument must be an HttpRequest object, not '
                "'%s'." % request.__class__.__name__
            )
        if not fail_silently:
            raise MessageFailure(
                'You cannot add messages without installing '
                'django.contrib.messages.middleware.MessageMiddleware'
            )
    else:
        return messages.add(level, message, extra_tags)


def add_alarm(request, level, message, extra_tags='', fail_silently=False):
    """
    Attempt to add a message to the request using the 'messages' app.
    """
    try:
        alarms = request._alarms
    except AttributeError:
        if not hasattr(request, 'META'):
            raise TypeError(
                'add_alarm() argument must be an HttpRequest object, not '
                "'%s'." % request.__class__.__name__
            )
        if not fail_silently:
            raise MessageFailure(
                'You cannot add alarms without installing '
                'bitcaster.middleware.messages.MessageMiddleware'
            )
    else:
        return alarms.add(level, message, extra_tags)
