import logging
import time
from typing import TYPE_CHECKING, Any

from django import db
from dramatiq import Middleware

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from dramatiq import Broker, MessageProxy


class WorkerHeartbeatMiddleware(Middleware):
    def before_process_message(self, broker: "Broker", message: "MessageProxy") -> None:
        logger.debug(f"START {message.actor_name} {message, type(message)}")
        from .manager import BackgroundManager

        message.options["started_at"] = int(time.time() * 1000)
        manager = BackgroundManager()
        try:
            manager.register_task(message)
        except Exception:
            raise

    def after_process_message(
        self,
        broker: "Broker",
        message: "MessageProxy",
        *,
        result: Any | None = None,
        exception: BaseException | None = None,
    ) -> None:
        logger.debug(f"END {message.actor_name} {message, type(message)}")
        from .manager import BackgroundManager

        manager = BackgroundManager()

        try:
            manager.unregister_task(message)
        except Exception:
            raise


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
