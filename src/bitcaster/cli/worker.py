import logging
from typing import TYPE_CHECKING, Any

import click
from colorlog import ColoredFormatter
from dramatiq import Middleware

from bitcaster.runner.manager import BackgroundManager

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from dramatiq import Broker, Message, MessageProxy

LOGFORMAT = "%(log_color)s%(asctime)s%(reset)s | %(log_color)s%(message)s%(reset)s"


class ClickMiddleware(Middleware):
    def before_enqueue(self, broker: "Broker", message: "Message[Any]", delay: int) -> None:
        click.echo(f"Enqueueing...{message.actor_name}")

    def before_ack(self, broker: "Broker", message: "MessageProxy") -> None:
        click.echo(f"Ack...{message.actor_name}")

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


def runit(args: list[str]) -> None:
    from dramatiq.cli import make_argument_parser

    from bitcaster.runner.config import dramatiq
    from bitcaster.runner.manager import BackgroundManager

    manager = BackgroundManager()
    manager.register_runner()
    click.echo(" ".join(args))
    try:
        from bitcaster.runner.tasks import broker

        broker.middleware.append(ClickMiddleware())
        dramatiq.cli.main(make_argument_parser().parse_args(args))  # type: ignore[no-untyped-call]
    except KeyboardInterrupt:
        click.echo("Runner stopping...")
    finally:
        manager.unregister_runner()


@click.command()
@click.option("-p", "--processes", default=1, help="Enable/disable worker events (default: enabled)")
@click.option("-t", "--threads", default=1, help="Enable/disable worker events (default: enabled)")
@click.option("-d", "--debug", is_flag=True, help="")
@click.option("--reset", is_flag=True, help="")
@click.option("-v", "--verbose", count=True)
@click.option("--pid-file", type=click.Path())
@click.option("--autoreload", is_flag=True, default=False, help="Reload on code changes")
def run(
    processes: int, threads: int, verbose: bool, debug: bool, autoreload: bool, pid_file: str, reset: bool = False
) -> None:
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
        "bitcaster.runner.tasks",
    ]
    if verbose:
        args.append(
            "-" + "v" * verbose,
        )
    if pid_file:
        args.extend(["--pid-file", pid_file])

    log_level = logging.CRITICAL - (verbose * 10)
    if reset:
        manager = BackgroundManager()
        manager.reset()
    if debug:
        logging.getLogger("root").root.setLevel(logging.DEBUG)
        logging.getLogger("root").setLevel(logging.DEBUG)
        logging.getLogger("bitcaster").setLevel(logging.DEBUG)
        logging.getLogger("dramatiq").setLevel(logging.DEBUG)
        logging.getLogger("dramatiq.worker").setLevel(logging.DEBUG)
    else:
        stream = logging.StreamHandler()
        stream.setLevel(log_level)
        formatter = ColoredFormatter(LOGFORMAT)
        stream.setFormatter(formatter)
        for logger_name in ["dramatiq", "bitcaster", "dramatiq.worker"]:
            logger = logging.getLogger(logger_name)
            logger.setLevel(log_level)
            logger.setLevel(log_level)
            logger.addHandler(stream)
            logger.propagate = False
    if autoreload:
        from django.utils import autoreload as django_autoreload

        django_autoreload.run_with_reloader(runit, args)
    else:
        runit(args)
