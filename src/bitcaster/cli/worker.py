import logging.config
import os

import click
import dramatiq.cli


@click.command()
@click.option("-l", "--loglevel", default="info", help="Logging level (default: info)")
@click.option("-p", "--processes", default=1, help="Enable/disable worker events (default: enabled)")
@click.option("-t", "--threads", default=1, help="Enable/disable worker events (default: enabled)")
def run(loglevel: str, processes: int, threads: int) -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bitcaster.config.settings")
    import django

    django.setup()

    from django.conf import settings

    from bitcaster.config.dramatiq import broker

    logging.config.dictConfig(settings.DRAMATIQ_LOGGING)
    dramatiq.set_broker(broker)
    from dramatiq.cli import make_argument_parser

    args = [
        "dramatiq",
        "--path",
        ".",
        "--processes",
        str(processes),
        "--threads",
        str(threads),
        "--worker-shutdown-timeout",
        "600000",
        "--skip-logging",
        "bitcaster.tasks",
    ]
    if loglevel.lower() == "debug":
        args.append("-vv")
    elif loglevel.lower() == "info":
        args.append("-v")

    dramatiq.cli.main(make_argument_parser().parse_args(args))
