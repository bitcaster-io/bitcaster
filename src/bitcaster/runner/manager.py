import json
import logging
import os
from _socket import gethostname
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

import dramatiq
import msgpack
from apscheduler.schedulers.blocking import BlockingScheduler
from django_redis import get_redis_connection

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from dramatiq import MessageProxy


class BackgroundManager:
    def __init__(self) -> None:
        self.client = get_redis_connection("default")
        self.name = f"bitcaster@{gethostname()}"

    def get_executor_name(self) -> str:
        return f"{os.getpid()}"

    def get_queue_sizes(self) -> dict[str, int]:
        broker = dramatiq.get_broker()
        sizes: dict[str, int] = {}

        for queue in broker.get_declared_queues():
            key = f"{broker.namespace}:{queue}.msgs"
            if not broker.client.exists(key):
                sizes[queue] = 0
                continue

            key_type = broker.client.type(key).decode()
            if key_type == "list":
                sizes[queue] = broker.client.llen(key)
            elif key_type == "hash":
                sizes[queue] = broker.client.hlen(key)
            else:
                sizes[queue] = 0  # unknown type

        return sizes

    def get_queued_items(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        broker = dramatiq.get_broker()
        for queue in broker.get_declared_queues():
            key = f"{broker.namespace}:{queue}.msgs"
            if broker.client.exists(key):
                key_type = broker.client.type(key).decode()
                if key_type == "list":
                    raw_messages = broker.client.lrange(key, 0, -1)
                    for raw in raw_messages:
                        # If list uses msgpack
                        msg = msgpack.unpackb(raw, raw=False)
                        items.append(msg)
                elif key_type == "hash":
                    raw_messages = broker.client.hvals(key)
                    for raw in raw_messages:
                        raw_str = raw.decode() if isinstance(raw, bytes) else raw
                        msg = json.loads(raw_str)
                        items.append(msg)

        return items

    def reset(self) -> None:
        logger.debug("Resetting manager")
        cursor = 0
        while True:
            cursor, keys = self.client.scan(cursor=cursor, match="background:*", count=1000)
            if keys:
                self.client.delete(*keys)
            if cursor == 0:
                break

    def register_runner(self) -> None:
        logger.debug(f"Registering runner {self.name}")
        self.client.sadd("background:runners", self.name)
        return self.client.set(f"background:runner:{self.name}:last_seen", datetime.now(UTC).timestamp())

    def unregister_runner(self) -> None:
        logger.debug(f"Unregistering runner {self.name}")
        self.client.srem("background:runners", self.name)
        self.client.delete(f"background:runners:{self.name}:tasks")
        return self.client.delete(f"background:runners:{self.name}:last_seen")

    def get_runners(self) -> dict[str, Any]:
        items = self.client.smembers("background:runners")
        ret = {}
        for e in items:
            ts = float(self.client.get(f"background:runner:{e.decode()}:last_seen").decode())
            dt = datetime.fromtimestamp(ts, tz=UTC)
            tasks = self.client.hgetall(f"background:runners:{e.decode()}:tasks")
            ret[e.decode()] = {
                "tasks": sorted([json.loads(v.decode()) for k, v in tasks.items()], key=lambda t: t["pid"]),
                "last_seen": dt.strftime("%Y-%m-%d %H:%M:%S"),
            }
        return ret

    def register_task(self, message: "MessageProxy") -> None:
        self.register_runner()
        task_info = json.dumps(
            {
                "id": message.message_id,
                "executor": self.name,
                "ppid": os.getppid(),
                "pid": os.getpid(),
                "name": message.actor_name,
                "started_at": message.options.get("started_at", None),
                "enqueued_at": message.message_timestamp,
            }
        )
        return self.client.hset(f"background:runners:{self.name}:tasks", self.get_executor_name(), task_info)

    def unregister_task(self, message: "MessageProxy") -> None:
        return self.client.hdel(f"background:runners:{self.name}:task", self.get_executor_name())

    def scheduler_ping(self) -> None:
        self.client.set("scheduler:alive", datetime.now(UTC).isoformat())

    def scheduler_info(self) -> dict[str, Any]:
        ts = self.client.get("scheduler:alive")
        if not ts:
            return {"status": False, "seen": ""}
        return {
            "status": datetime.now(UTC) - datetime.fromisoformat(ts.decode()) < timedelta(minutes=1),
            "seen": ts.decode(),
        }


scheduler = BlockingScheduler()
