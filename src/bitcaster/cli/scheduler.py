from typing import TYPE_CHECKING

import click
from celery.utils.nodenames import gethostname
from django.conf import settings
from django.core.cache import cache

from bitcaster.cli import lock_key

if TYPE_CHECKING:
    from celery.apps.beat import Beat


@click.command()
@click.option("-l", "--loglevel", default="info", help="Logging level (default: info)")
def scheduler(loglevel: str, scheduler: str | None = None) -> None:
    """Run Celery Beat as a dedicated process.

    Only one Beat process will run at a time using Django cache lock.
    """
    from bitcaster.config.celery import app

    lock_timeout = 60  # seconds
    if not cache.add(lock_key, gethostname(), lock_timeout):
        click.echo("Another Scheduler instance is already running. Exiting.")
        return

    options = {
        "loglevel": loglevel,
        "scheduler": settings.CELERY_BEAT_SCHEDULER,
        "pidfile": None,
        "detach": False,
    }

    click.echo("Starting dedicated Scheduler...")
    beat_instance: "Beat" = app.Beat(**options)
    try:
        beat_instance.run()
    finally:
        cache.delete(lock_key)
