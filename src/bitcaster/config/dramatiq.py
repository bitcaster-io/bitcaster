import dramatiq
from django.conf import settings
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import AgeLimit, CurrentMessage, Middleware, Retries, ShutdownNotifications, TimeLimit

SECOND = 1000
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24


class AdminMiddleware(Middleware):
    def after_enqueue(self, broker, message, delay):
        pass

    def after_dequeue(self, broker, message):
        pass

    def before_enqueue(self, broker, message, delay):
        pass

    def before_process_message(self, broker, message):
        pass

    def after_process_message(self, broker, message, *, result=None, exception=None, status=None):
        pass


# Replace `dramatiq.Broker` with a concrete class, e.g. dramatiq.brokers.redis.RedisBroker.
broker = RedisBroker(
    url=settings.DRAMATIQ_BROKER,
    middleware=[
        AgeLimit(),
        TimeLimit(time_limit=HOUR * 3, interval=MINUTE),
        ShutdownNotifications(),
        # Note: custom default max_retries of 5
        Retries(max_retries=5),
        # Note: non-default middleware class included.
        CurrentMessage(),
        # Note: Callbacks and Pipelines are not included.
        # They will not be added back by dramatiq.
    ],
)

dramatiq.set_broker(broker)
