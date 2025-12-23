from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from click.core import Context


@click.group()
@click.option("--debug", default=False, is_flag=True, envvar="BITCASTER_DEBUG")
@click.pass_context
def cli(ctx: "Context", debug: bool) -> None:
    try:
        ctx.obj = {"debug": debug}
    except Exception as e:
        raise click.ClickException(f"Failed to initialize Bitcaster. {e}") from None


def register_commands() -> None:
    from .queue import queues
    from .scheduler import scheduler
    from .worker import run

    cli.add_command(run)
    cli.add_command(scheduler)
    cli.add_command(queues)


register_commands()
