import os

import click
import django
from apscheduler import events


@click.command()
@click.option("-l", "--loglevel", default="info", help="Logging level (default: info)")
def scheduler(loglevel: str, scheduler_name: str | None = None) -> None:
    """Run Celery Beat as a dedicated process.

    Only one Beat process will run at a time using Django cache lock.
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bitcaster.config.settings")
    django.setup()

    from bitcaster.tasks import beat_heartbeat, scan_occurrences, scheduler

    def xxx(event: events.SchedulerEvent):
        match event.code:
            case events.EVENT_EXECUTOR_ADDED:
                _ = "EVENT_EXECUTOR_ADDED"  # noqa: F841
            case events.EVENT_JOBSTORE_ADDED:
                _ = "EVENT_JOBSTORE_ADDED"  # noqa: F841
            case events.EVENT_JOB_ADDED:
                _ = f"EVENT_JOB_ADDED {event.job_id}"  # noqa: F841
            case events.EVENT_JOB_EXECUTED:
                _ = f"EVENT_JOB_EXECUTED {event.job_id}"  # noqa: F841
            case events.EVENT_JOB_SUBMITTED:
                _ = f"EVENT_JOB_SUBMITTED {event.job_id}"  # noqa: F841
            case events.EVENT_JOB_ERROR:
                _ = f"EVENT_JOB_ERROR {event.job_id}"  # noqa: F841
            case events.EVENT_SCHEDULER_START:
                _ = "EVENT_SCHEDULER_START"  # noqa: F841
            case events.EVENT_SCHEDULER_SHUTDOWN:
                _ = "EVENT_SCHEDULER_SHUTDOWN"  # noqa: F841
            case __:
                _ = "??"  # noqa: F841

    scheduler.add_listener(xxx)

    scheduler.add_job(
        id="beat_heartheart",  # Corrected typo in id
        func=lambda: beat_heartbeat.send(),
        trigger="interval",
        seconds=10,
        replace_existing=True,
    )
    scheduler.add_job(
        id="scan_occurrences",
        func=lambda: scan_occurrences.send(),
        trigger="interval",
        seconds=10,
        replace_existing=True,
    )
    try:
        click.echo("Scheduler started... Press Ctrl+C to exit")
        scheduler.start()
    except KeyboardInterrupt:
        click.echo("Scheduler stopping...")
        scheduler.shutdown()
