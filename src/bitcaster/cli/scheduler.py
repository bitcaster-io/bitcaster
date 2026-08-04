import datetime
import logging
import os

import click
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, JobExecutionEvent
from sentry_sdk.utils import epoch

import django
from django.utils.module_loading import import_string

from .utils import configure_logging
from ..models import Task
from ..runner.manager import BackgroundManager, init_scheduler, scheduler

logger = logging.getLogger(__name__)

last_round = epoch.astimezone(datetime.UTC)


def queue(task_id: int) -> None:
    task = Task.objects.get(id=task_id)
    # Security: Validate against a whitelist of allowed actors
    allowed_actors = BackgroundManager().get_all_tasks().keys()
    if task.func not in allowed_actors:
        logger.error(f"Security Alert: Blocked execution of unverified task function {task.func}")
        return

    logger.warning(f"queued {task.name}")
    actor = import_string(task.func)
    actor.send()


def healthcheck() -> bool:
    logger.warning("Healthcheck")
    BackgroundManager().scheduler_ping()
    return True


def job_listener(event: JobExecutionEvent) -> None:
    if event.exception:
        logger.error(f"Job {event.job_id} failed: {event.exception}")
    else:
        logger.info(f"Job {event.job_id} executed (returned {event.retval!r})")


def dump_schedule() -> None:
    click.echo("Current scheduling:")
    for job in scheduler.get_jobs():
        next_run = getattr(job, "next_run_time", None)
        click.echo(f"  - {job.id:<25} {job.trigger}  next: {next_run}")


def inspect_jobs() -> bool:
    global last_round  # noqa: PLW0603
    for task in Task.objects.filter(last_updated__gt=last_round):
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
                next_run_time = getattr(job, "next_run_time", None)
                if not task.active and next_run_time:
                    job.pause()
                    logger.warning(f"{job.id} paused")
                elif task.active and not next_run_time:
                    job.resume()
                    logger.warning(f"{job.id} resumed")
                else:  # task.active and next_run_time:
                    scheduler.remove_job(job.id)
                    job = scheduler.add_job(**kwargs)
                    logger.warning(f"UPDATED {job.id} / {task.slug}")
            else:
                job = scheduler.add_job(**kwargs)
                if not task.active:
                    job.pause()
                logger.warning(f"ADDED {job.id} ({task.get_status()}) {task.scheduling()}")

        except Exception:
            logger.exception(f"ERROR processing task {task.slug}")
    last_round = datetime.datetime.now(datetime.UTC)
    return True


def run_scheduler(verbose: int, debug: bool) -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bitcaster.config.settings")
    django.setup()

    if debug:
        log_level = logging.DEBUG
    elif verbose > 0:
        log_level = logging.CRITICAL - (verbose * 10)
    else:
        log_level = logging.CRITICAL

    if debug:
        comp_log_level = log_level
    else:
        comp_log_level = logging.ERROR
    configure_logging(log_level, comp_log_level)
    click.echo(f"Logging level set to {logging._levelToName[log_level]} / {logging._levelToName[comp_log_level]} ")

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
    healthcheck()
    init_scheduler()

    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    try:
        inspect_jobs()
        dump_schedule()
        scheduler.start()
    except KeyboardInterrupt:
        click.echo("Scheduler stopping...")
        if scheduler.running:
            scheduler.shutdown()


@click.command(name="scheduler")
@click.option("-d", "--debug", is_flag=True, help="Enable debug logging")
@click.option("-v", "--verbose", count=True, default=3, help="Increase verbosity (use -vv for more detail)")
@click.option("--autoreload", is_flag=True, help="Reload on code changes")
def cron(verbose: int, debug: bool, autoreload: bool) -> None:
    """Run the task scheduler."""
    if autoreload:
        from django.utils import autoreload as django_autoreload

        django_autoreload.run_with_reloader(run_scheduler, verbose=verbose, debug=debug)
    else:
        run_scheduler(verbose=verbose, debug=debug)
