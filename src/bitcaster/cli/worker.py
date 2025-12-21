import os
from typing import TYPE_CHECKING

import click
from celery.utils.nodenames import gethostname, host_format
from django.conf import settings
from django.core.cache import cache

from bitcaster.cli import lock_key

if TYPE_CHECKING:
    from celery.apps.worker import Worker


@click.command()
@click.option("-l", "--loglevel", default="info", help="Logging level (default: info)")
@click.option("--events/--no-events", "events", default=True, help="Enable/disable worker events (default: enabled)")
@click.option("--concurrency", default=4, type=int, help="Number of child processes processing the queue")
@click.option("--scheduler/--no-scheduler", "scheduler", default=True, help="Embedded Beat Options")
@click.option("--queues", default=None, help="List of queues to enable for this worker")
def run(events: bool, loglevel: str, scheduler: bool, concurrency: int, queues: str | None) -> None:
    """Start background process manager."""
    from bitcaster.config.celery import app

    run_beat = scheduler
    if scheduler:
        lock_timeout = 60  # seconds
        if not cache.add(lock_key, gethostname(), lock_timeout):
            click.echo("Scheduler lock held by another worker. Skipping Scheduler.")
            run_beat = False  # another worker is running Beat
        else:
            click.echo("Acquired lock. Starting Scheduler.")

    options = {
        "hostname": host_format(f"bitcaster-{os.getpid()}", "bitcaster", gethostname()),
        "loglevel": loglevel,
        "concurrency": concurrency,
        "traceback": True,
        "without_gossip": True,
        "without_mingle": True,
        "task_events": events,
        "pool": "prefork",
        "statedb": None,
        "beat": run_beat,
        "scheduler": settings.CELERY_BEAT_SCHEDULER,
    }

    if queues:
        options["queues"] = queues

    w: "Worker" = app.Worker(**options)
    w.start()
