import logging

import click

from .utils import configure_logging
from ..runner.manager import BackgroundManager

logger = logging.getLogger(__name__)

LOGFORMAT = "%(log_color)s%(asctime)s%(reset)s | %(log_color)s%(message)s%(reset)s"


def runit(args: list[str], log_level, comp_log_level, **extra) -> None:
    from dramatiq.cli import make_argument_parser

    from .utils import configure_logging
    from ..runner.config import dramatiq

    click.echo(" ".join(args))
    try:
        configure_logging(log_level, comp_log_level)
        dramatiq.cli.main(make_argument_parser().parse_args(args))  # type: ignore[no-untyped-call]
    except KeyboardInterrupt:
        click.echo("Runner stopping...")


@click.command()
@click.option("-p", "--processes", default=1, help="Number of worker processes")
@click.option("-t", "--threads", default=1, help="Number of worker threads per process")
@click.option("-d", "--debug", is_flag=True, help="Enable debug logging")
@click.option("--reset", is_flag=True, help="Clear pending tasks from all queues")
@click.option("-v", "--verbose", count=True, default=0, help="Increase verbosity (use -vv for more detail)")
@click.option("--pid-file", type=click.Path(), help="Write PID to this file")
@click.option("--autoreload", is_flag=True, default=False, help="Reload on code changes")
def run(
    processes: int, threads: int, verbose: bool, debug: bool, autoreload: bool, pid_file: str, reset: bool = False
) -> None:
    """Run background task workers."""
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

    if debug:
        comp_log_level = log_level
    else:
        comp_log_level = logging.ERROR
    configure_logging(log_level, comp_log_level)
    if reset:
        manager = BackgroundManager()
        manager.reset()

    if autoreload:
        from django.utils import autoreload as django_autoreload

        django_autoreload.run_with_reloader(runit, args, log_level=log_level, comp_log_level=comp_log_level)
    else:
        runit(args, log_level=log_level, comp_log_level=comp_log_level)
