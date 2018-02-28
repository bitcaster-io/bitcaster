import itertools
import logging
import random
import time

from django.utils.encoding import force_bytes

logger = logging.getLogger(__name__)


class RetryException(Exception):
    def __init__(self, message, exception):
        self.message = message
        self.exception = exception

    def __str__(self):
        return force_bytes(self.message, errors='replace')

    def __repr__(self):
        return u'<{}: {!r}>'.format(
            type(self).__name__,
            self.message,
        )


class RetryPolicy(object):
    def __call__(self, function):
        raise NotImplementedError


class TimedRetryPolicy:
    """
    A time-based policy that can be used to retry a callable in the case of
    failure as many times as possible up to the ``timeout`` value (in seconds.)

    The ``delay`` function accepts one argument, a number which represents the
    number of this attempt (starting at 1.)
    """

    def __init__(self, timeout, func, delay=None, exceptions=(Exception,)):
        if delay is None:
            # 100ms +/- 50ms of randomized jitter
            delay = lambda i: 0.1 + ((random.random() - 0.5) / 10)

        self.timeout = timeout
        self.delay = delay
        self.exceptions = exceptions
        self.clock = time
        self.function = func

    # def __enter__(self):
    #     pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __enter__(self):
        start = self.clock.time()
        for i in itertools.count(1):
            try:
                return self.function()
            except self.exceptions as error:
                delay = self.delay(i)
                now = self.clock.time()
                if (now + delay) > (start + self.timeout):
                    raise RetryException(
                        'Could not successfully execute %r within %.3f seconds (%s attempts.)' % (
                            self.function, now - start, i),
                        error,
                    )
                else:
                    logger.debug(
                        'Failed to execute %r due to %r on attempt #%s, retrying in %s seconds...',
                        self.function,
                        error,
                        i,
                        delay,
                    )
                    self.clock.sleep(delay)
