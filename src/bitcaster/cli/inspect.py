import os

import click
import django
import dramatiq

# The `TYPE_CHECKING` and `apscheduler.events` imports were removed as they were unused.


@click.command()
@click.option("-l", "--loglevel", default="info", help="Logging level (default: info)")
def inspect(loglevel: str, scheduler: str | None = None) -> None:
    # Initialize Django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bitcaster.config.settings")
    django.setup()

    # Import tasks to register actors
    from bitcaster.runner import tasks  # noqa: F401

    broker = dramatiq.get_broker()
    print("Registered Dramatiq Actors:")  # noqa: T201
    for actor_name in broker.get_declared_actors():
        actor = broker.get_actor(actor_name)
        print(f"- {actor.actor_name} ({actor.queue_name})")  # noqa: T201
