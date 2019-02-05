from functools import partial

from django.contrib.messages import MessageFailure, constants

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


def add(target, request, level, message, extra_tags='', fail_silently=False):
    try:
        targets = getattr(request, target)
    except AttributeError:  # pragma: no cover
        if not hasattr(request, 'META'):
            raise TypeError(
                'add() argument must be an HttpRequest object, not '
                "'%s'." % request.__class__.__name__
            )
        if not fail_silently:
            raise MessageFailure(
                'You cannot add alarms/messages without installing '
                'bitcaster.middleware.messages.MessageMiddleware'
            )
    else:
        return targets.add(level, message, extra_tags)


add_alarm = partial(add, '_alarms')
add_message = partial(add, '_messages')


class Wrapper:
    def __init__(self, target_name):
        self.target_name = target_name

    def debug(self, request, message, extra_tags='', fail_silently=False):
        """Add a message with the ``DEBUG`` level."""
        add(self.target_name, request, constants.DEBUG, message, extra_tags=extra_tags,
            fail_silently=fail_silently)

    def info(self, request, message, extra_tags='', fail_silently=False):
        """Add a message with the ``INFO`` level."""
        add(self.target_name,
            request, constants.INFO, message, extra_tags=extra_tags,
            fail_silently=fail_silently)

    def success(self, request, message, extra_tags='', fail_silently=False):
        """Add a message with the ``SUCCESS`` level."""
        add(self.target_name, request, constants.SUCCESS, message, extra_tags=extra_tags,
            fail_silently=fail_silently)

    def warning(self, request, message, extra_tags='', fail_silently=False):
        """Add a message with the ``WARNING`` level."""
        add(self.target_name, request, constants.WARNING, message, extra_tags=extra_tags,
            fail_silently=fail_silently)

    def error(self, request, message, extra_tags='', fail_silently=False):
        """Add a message with the ``ERROR`` level."""
        add(self.target_name, request, constants.ERROR, message, extra_tags=extra_tags,
            fail_silently=fail_silently)


msgs = Wrapper('_messages')
alarms = Wrapper('_alarms')
