import django.contrib.postgres.indexes
import dramatiq
from django.db import migrations

from bitcaster.runner.tasks import SmartActor


@dramatiq.actor(actor_class=SmartActor)
def sample_task():
    pass
