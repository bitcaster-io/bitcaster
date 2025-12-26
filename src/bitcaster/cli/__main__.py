import logging
import logging.config
import os
from typing import TYPE_CHECKING

import click
import django
from django.conf import settings

if TYPE_CHECKING:
    from click.core import Context

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bitcaster.config.settings")
    logging.config.dictConfig(settings.DRAMATIQ_LOGGING)
    django.setup()
except Exception as e:
    raise click.ClickException(f"Failed to initialize Bitcaster. {e}") from None


@click.group()
@click.option("--debug", default=False, is_flag=True, envvar="BITCASTER_DEBUG")
@click.pass_context
def cli(ctx: "Context", debug: bool) -> None:
    """Provide a command line interface for Bitcaster."""
    ctx.obj = {"debug": debug}


def register_commands() -> None:
    from .inspect import inspect
    from .queue import queue
    from .scheduler import cron
    from .worker import run

    cli.add_command(run)
    cli.add_command(inspect)
    cli.add_command(cron)
    cli.add_command(queue)


register_commands()
