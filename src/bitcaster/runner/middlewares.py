from typing import TYPE_CHECKING, Any

import logging
import time

from dramatiq import Message, Middleware, Worker

from django import db

from bitcaster.runner.manager import BackgroundManager

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from dramatiq import Actor, Broker, MessageProxy


class WorkerHeartbeatMiddleware(Middleware):
    def before_process_message(self, broker: "Broker", message: "MessageProxy") -> None:
        logger.debug(f"START {message.actor_name}")
        message.options["started_at"] = int(time.time() * 1000)
        BackgroundManager().register_task(message)

    def after_process_message(
        self,
        broker: "Broker",
        message: "MessageProxy",
        *,
        result: Any | None = None,
        exception: BaseException | None = None,
    ) -> None:
        logger.debug(f"END {message.actor_name}")
        BackgroundManager().unregister_task(message)


class DbConnectionsMiddleware(Middleware):
    def _close_old_connections(self, *args: Any, **kwargs: Any) -> None:
        db.close_old_connections()

    before_process_message = _close_old_connections
    after_process_message = _close_old_connections

    def _close_connections(self, *args: Any, **kwargs: Any) -> None:
        db.connections.close_all()

    before_consumer_thread_shutdown = _close_connections
    before_worker_thread_shutdown = _close_connections
    before_worker_shutdown = _close_connections


class ClickMiddleware(Middleware):
    @property
    def actor_options(self) -> set[str]:
        return {"logging", "start"}

    def before_worker_boot(self, broker: "Broker", worker: "Worker") -> None:
        pass

    def after_worker_boot(self, broker: "Broker", worker: "Worker") -> None:
        BackgroundManager().register_runner()

    def before_enqueue(self, broker: "Broker", message: "Message[Any]", delay: int) -> None:
        pass

    def before_ack(self, broker: "Broker", message: "MessageProxy") -> None:
        pass

    def before_process_message(self, broker: "Broker", message: "MessageProxy") -> None:
        message.options["start"] = time.perf_counter()

    def after_process_message(
        self,
        broker: "Broker",
        message: "MessageProxy",
        *,
        result: Any | None = None,
        exception: BaseException | None = None,
    ) -> None:
        delta = time.perf_counter() - message.options["start"]
        actor: "Actor[Any, Any]" = broker.get_actor(message.actor_name)
        do_logging = message.options.get("logging") or actor.options.get("logging")
        if do_logging:
            from bitcaster.models import ProcessLogEntry

            ProcessLogEntry.objects.log_process(
                actor, elapsed=delta, error=exception, args=message._message.args, kwargs=message._message.kwargs
            )
