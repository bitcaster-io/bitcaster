from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

import click
from redis import Redis

if TYPE_CHECKING:
    from celery import Celery
    from celery.app.control import Inspect


@dataclass(slots=True)
class QueueStats:
    waiting: int | None = None
    error: str | None = None


@dataclass(slots=True)
class WorkerSection:
    tasks: dict[str, list[dict[str, object]]]


@dataclass(slots=True)
class CeleryStatus:
    broker: str
    queues: dict[str, QueueStats]
    workers: dict[str, WorkerSection]


# =============================
# Celery app loader (Django-safe)
# =============================
def get_celery_app() -> Celery:
    from bitcaster.config.celery import app

    return app


# =============================
# CLI command
# =============================
@click.command(help="Show Celery queue status (Redis broker only)")
@click.option(
    "--queues",
    default=None,
    help="Comma-separated queue names (default: celery)",
)
@click.option(
    "--json-output",
    is_flag=True,
    help="Output JSON (machine readable)",
)
def queues(queues: str | None, json_output: bool) -> None:
    app: Celery = get_celery_app()
    inspect: Inspect = app.control.inspect(timeout=2)

    queue_names: list[str] = (
        [q.strip() for q in queues.split(",")] if queues else [app.conf.task_default_queue or "celery"]
    )

    status = CeleryStatus(
        broker=str(app.conf.broker_url),
        queues={},
        workers={},
    )

    _collect_worker_state(inspect, status)
    _collect_redis_queues(app, queue_names, status)

    if json_output:
        click.echo(json.dumps(_serialize(status), indent=2))
    else:
        _print_human(status)


# =============================
# Worker inspection
# =============================
def _collect_worker_state(inspect: Inspect, status: CeleryStatus) -> None:
    sections: Final[tuple[str, ...]] = ("active", "reserved", "scheduled")

    for section in sections:
        result = getattr(inspect, section)()
        status.workers[section] = WorkerSection(tasks=result or {})


def _collect_redis_queues(
    app: Celery,
    queue_names: list[str],
    status: CeleryStatus,
) -> None:
    redis_url: str = str(app.conf.broker_url)
    redis: Redis[str] = Redis.from_url(redis_url, decode_responses=True)

    for queue in queue_names:
        try:
            waiting: int = redis.llen(queue)
            status.queues[queue] = QueueStats(waiting=waiting)
        except Exception as exc:  # noqa: BLE001 (intentional)
            status.queues[queue] = QueueStats(error=str(exc))


def _serialize(status: CeleryStatus) -> dict[str, object]:
    return {
        "broker": status.broker,
        "queues": {
            name: {
                "waiting": q.waiting,
                "error": q.error,
            }
            for name, q in status.queues.items()
        },
        "workers": {
            section: {worker: len(tasks) for worker, tasks in data.tasks.items()}
            for section, data in status.workers.items()
        },
    }


def _print_human(status: CeleryStatus) -> None:
    click.echo(click.style("\n📦 Broker", bold=True))
    click.echo(f"  {status.broker}")

    click.echo(click.style("\n📬 Queues", bold=True))
    for name, info in status.queues.items():
        click.echo(f"  • {name}")
        if info.waiting is not None:
            click.echo(f"      waiting: {info.waiting}")
        if info.error:
            click.echo(click.style(f"      error: {info.error}", fg="red"))

    click.echo(click.style("\n👷 Workers", bold=True))
    for section, data in status.workers.items():
        click.echo(f"\n  {section}:")
        if not data.tasks:
            click.echo("    (none)")
            continue
        for worker, tasks in data.tasks.items():
            click.echo(f"    {worker}: {len(tasks)}")
