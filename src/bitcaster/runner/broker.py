from django.conf import settings
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import CurrentMessage, Retries, ShutdownNotifications

from .middlewares import DbConnectionsMiddleware, WorkerHeartbeatMiddleware

broker: RedisBroker = RedisBroker(  # type: ignore[no-untyped-call]
    url=settings.DRAMATIQ_BROKER,
    namespace="bitcaster",
    middleware=[
        WorkerHeartbeatMiddleware(),
        ShutdownNotifications(),
        # # Note: custom default max_retries of 5
        Retries(max_retries=5),
        # # Note: non-default middleware class included.
        CurrentMessage(),
        DbConnectionsMiddleware(),
    ],
)
