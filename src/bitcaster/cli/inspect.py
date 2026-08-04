import os

import click

import django

from ..runner.manager import BackgroundManager


@click.command()
@click.option("-l", "--loglevel", default="info", help="Logging level (default: info)")
def inspect(loglevel: str, scheduler: str | None = None) -> None:
    """Inspect registered background tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bitcaster.config.settings")
    django.setup()

    from ..runner import tasks  # noqa: F401

    for task_func, task_name in BackgroundManager().get_all_tasks().items():
        print(f"- {task_name:<40} {task_func}")  # noqa: T201
