import os
from typing import TYPE_CHECKING, Any

import click
import django
from django.utils import timezone
from django.utils.module_loading import import_string

if TYPE_CHECKING:
    from dramatiq import Actor


def echo(message: str, fg: str = "yellow") -> None:
    ts = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    click.secho(f"{ts} - {message}", fg=fg)


@click.command(name="scheduler")
@click.option("-l", "--loglevel", default="info", help="Logging level (default: info)")
def cron(loglevel: str, scheduler_name: str | None = None) -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bitcaster.config.settings")
    django.setup()
    from bitcaster.runner.config import SCHEDULER
    from bitcaster.runner.manager import BackgroundManager, scheduler

    def healthcheck() -> None:
        echo("Healthcheck", fg="yellow")
        BackgroundManager().scheduler_ping()

    def queued(func: "Actor[Any, Any]") -> None:
        echo(f"Queued {func.actor_name}", fg="yellow")
        func.send()

    scheduler.add_job(
        id="scheduler_ping",  # Corrected typo in id
        func=healthcheck,
        trigger="interval",
        seconds=10,
        replace_existing=True,
    )
    for name, config in SCHEDULER.items():
        click.echo(f"Adding job {name}")
        if isinstance(config["func"], str):
            f = import_string(config["func"])
        elif callable(config["func"]):
            f = config["func"]
        else:
            continue
        entry = {**config, "id": name, "func": lambda: queued(f)}  # noqa B023
        scheduler.add_job(**entry)

    try:
        click.echo("Scheduler started... Press Ctrl+C to exit")
        healthcheck()
        scheduler.start()
    except KeyboardInterrupt:
        click.echo("Scheduler stopping...")
        scheduler.shutdown()
