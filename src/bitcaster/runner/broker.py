import sys
import time
from typing import TYPE_CHECKING, Any

from django.conf import settings
from dramatiq import Middleware
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import CurrentMessage, Retries, ShutdownNotifications

from .middlewares import DbConnectionsMiddleware, WorkerHeartbeatMiddleware

if TYPE_CHECKING:
    from dramatiq import Broker, Message, MessageProxy, Worker


class ClickMiddleware(Middleware):
    @property
    def actor_options(self) -> set[str]:
        return {"logging"}

    def before_worker_boot(self, broker: "Broker", worker: "Worker") -> None:
        pass

    def after_worker_boot(self, broker: "Broker", worker: "Worker") -> None:
        pass

    def before_enqueue(self, broker: "Broker", message: "Message[Any]", delay: int) -> None:
        pass

    def before_ack(self, broker: "Broker", message: "MessageProxy") -> None:
        pass

    def before_process_message(self, broker: "Broker", message: "MessageProxy") -> None:
        message._start = time.perf_counter()

    def after_process_message(
        self,
        broker: "Broker",
        message: "MessageProxy",
        *,
        result: Any | None = None,
        exception: BaseException | None = None,
    ) -> None:
        delta = time.perf_counter() - message._start
        actor = broker.get_actor(message.actor_name)
        logging = message.options.get("logging") or actor.options.get("logging")
        if logging:
            from bitcaster.models import ProcessLogEntry

            ProcessLogEntry.objects.log_process(
                self.fn, elapsed=delta, error=exception, args=message._message.args, kwargs=message._message.kwargs
            )

        sys.stdout.write(f"1111.1, {message._message}\n")
        sys.stdout.write(f"1111.2, {message.actor_name}\n")
        sys.stdout.write(f"1111.3, {message._message.args}\n")
        sys.stdout.write(f"1111.4, {message._message.kwargs}\n")
        sys.stdout.write(f"1111.4, {message._message.options}\n")


broker: RedisBroker = RedisBroker(  # type: ignore[no-untyped-call]
    url=settings.DRAMATIQ_BROKER,
    namespace="bitcaster",
    middleware=[
        WorkerHeartbeatMiddleware(),
        ShutdownNotifications(),
        ClickMiddleware(),
        # # Note: custom default max_retries of 5
        Retries(max_retries=5),
        # # Note: non-default middleware class included.
        CurrentMessage(),
        DbConnectionsMiddleware(),
    ],
)
