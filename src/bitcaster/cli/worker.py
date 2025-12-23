import logging
from typing import TYPE_CHECKING, Any

import click
from dramatiq import Middleware

if TYPE_CHECKING:
    from dramatiq import Broker, MessageProxy


@click.command()
@click.option("-l", "--loglevel", default="info", help="Logging level (default: info)")
@click.option("-p", "--processes", default=1, help="Enable/disable worker events (default: enabled)")
@click.option("-t", "--threads", default=1, help="Enable/disable worker events (default: enabled)")
@click.option("-d", "--debug", is_flag=True, help="")
@click.option("--dry-run", is_flag=True, help="")
def run(loglevel: str, processes: int, threads: int, dry_run: bool, debug: bool) -> None:
    args = [
        "--path",
        ".",
        "--processes",
        str(processes),
        "--threads",
        str(threads),
        "--worker-shutdown-timeout",
        "600000",
        "--skip-logging",
        # "--pid-file",
        # "bitcaster.pid",
        "bitcaster.runner.tasks",
    ]
    if loglevel.lower() == "debug":
        args.append("-vv")
    elif loglevel.lower() == "info":
        args.append("-v")

    from dramatiq.cli import make_argument_parser

    if debug:
        logging.getLogger("root").root.setLevel(logging.DEBUG)
        logging.getLogger("root").setLevel(logging.DEBUG)
        logging.getLogger("bitcaster").setLevel(logging.DEBUG)
    else:
        logging.getLogger("root").setLevel(logging.CRITICAL)
        logging.getLogger("bitcaster").setLevel(logging.CRITICAL)

    from bitcaster.runner.config import dramatiq
    from bitcaster.runner.manager import BackgroundManager

    manager = BackgroundManager()
    manager.register_runner()

    class ClickMiddleware(Middleware):
        def before_process_message(self, broker: "Broker", message: "MessageProxy") -> None:
            click.echo(f"Starting...{message.actor_name}")

        def after_process_message(
            self,
            broker: "Broker",
            message: "MessageProxy",
            *,
            result: "Any|None" = None,
            exception: BaseException | None = None,
        ) -> None:
            click.echo(f"Completed...{message.actor_name}")

    try:
        from bitcaster.runner.tasks import broker

        broker.middleware.append(ClickMiddleware())
        dramatiq.cli.main(make_argument_parser().parse_args(args))  # type: ignore[no-untyped-call]
    except KeyboardInterrupt:
        click.echo("Runner stopping...")
    finally:
        manager.unregister_runner()
