import datetime
import logging
import os
from typing import TYPE_CHECKING

import click
import django
from colorlog import ColoredFormatter
from django.utils import timezone
from django.utils.module_loading import import_string
from sentry_sdk.utils import epoch

from bitcaster.runner.manager import init_scheduler

if TYPE_CHECKING:
    from apscheduler.job import Job


logger = logging.getLogger(__name__)


def echo(message: str, fg: str = "yellow") -> None:
    ts = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    click.secho(f"{ts} - {message}", fg=fg)


LOGFORMAT = "%(log_color)s%(asctime)s%(reset)s | %(log_color)s%(message)s%(reset)s"


def run_scheduler(verbose: int, debug: bool) -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bitcaster.config.settings")
    django.setup()

    from bitcaster.models import Task
    from bitcaster.runner.manager import BackgroundManager, scheduler

    last_round = epoch.astimezone(datetime.UTC)
    job: Job

    def healthcheck() -> bool:
        logger.info("Healthcheck")
        BackgroundManager().scheduler_ping()
        return True

    def queue(task_id: int) -> None:
        task = Task.objects.get(id=task_id)
        actor = import_string(task.func)
        actor.send()

    def inspect_jobs() -> bool:
        nonlocal last_round
        logger.info(f"inspect_jobs {last_round}")
        for task in Task.objects.filter(last_updated__gt=last_round):
            logger.debug(f"Inspecting task {task}")
            try:
                kwargs = {
                    "id": task.slug,
                    "func": queue,
                    "args": [task.id],
                    "trigger": task.trigger,
                    "replace_existing": task.replace_existing,
                    "max_instances": task.max_instances,
                    **task.trigger_config,
                }

                if job := scheduler.get_job(task.slug):
                    logger.debug(f"processing {job}")
                    if not task.active and job.next_run_time:
                        job.pause()
                        logger.debug(f"{job.id} paused")
                    elif not job.next_run_time and task.active:
                        job.resume()
                        logger.debug(f"{job.id} resumed")
                    else:
                        scheduler.remove_job(job.id)
                        job = scheduler.add_job(**kwargs)
                        logger.debug(f"UPDATED {job.id} / {task.slug}")
                else:
                    job = scheduler.add_job(**kwargs)
                    if not task.active:
                        job.pause()
                    logger.debug(f"ADDED {job.id} ({task.get_status()}) {task.scheduling()}")

            except Exception as e:
                logger.error(f"ERROR {e}")
                raise
        last_round = datetime.datetime.now(datetime.UTC)
        return True

    if verbose > 0:
        log_level = logging.CRITICAL - (verbose * 10)
    else:
        log_level = logging.CRITICAL

    stream = logging.StreamHandler()
    stream.setLevel(log_level)
    formatter = ColoredFormatter(LOGFORMAT)
    stream.setFormatter(formatter)
    click.echo(f"Logging level set to {logging._levelToName[log_level]}")
    for logger_name in ["apscheduler", "bitcaster", "bitcaster.cli", "dramatiq"]:
        lg = logging.getLogger(logger_name)
        lg.setLevel(log_level)
        lg.addHandler(stream)
        lg.propagate = False

    scheduler.add_job(
        id="scheduler_ping",
        func=healthcheck,
        trigger="interval",
        minutes=1,
        replace_existing=True,
    )

    scheduler.add_job(
        id="inspect_jobs",
        func=inspect_jobs,
        trigger="interval",
        seconds=10,
        replace_existing=True,
    )
    init_scheduler()

    try:
        if log_level < logging.WARN:
            for job in scheduler.get_jobs():
                logger.warning(f"{job.name}")
        inspect_jobs()
        scheduler.start()
    except KeyboardInterrupt:
        click.echo("Scheduler stopping...")
        scheduler.shutdown()


@click.command(name="scheduler")
@click.option("-d", "--debug", is_flag=True, help="")
@click.option("-v", "--verbose", count=True)
@click.option("--autoreload", is_flag=True, help="Reload on code changes")
def cron(verbose: int, debug: bool, autoreload: bool) -> None:
    click.echo("Scheduler started... Press Ctrl+C to exit")
    if autoreload:
        from django.utils import autoreload as django_autoreload

        django_autoreload.run_with_reloader(run_scheduler, verbose=verbose, debug=debug)
    else:
        run_scheduler(verbose=verbose, debug=debug)
