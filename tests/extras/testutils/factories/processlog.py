import random
from typing import Any

import factory
from django.utils import timezone

from bitcaster.models import ProcessLogEntry
from bitcaster.runner.manager import BackgroundManager

from .base import AutoRegisterModelFactory


class ProcessLogEntryFactory(AutoRegisterModelFactory[ProcessLogEntry]):
    action_time = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())

    class Meta:
        model = ProcessLogEntry

    elapsed = factory.Faker("pyint", min_value=0, max_value=1000)
    status = ProcessLogEntry.SUCCESS

    @classmethod
    def create(cls, **kwargs: Any) -> "ProcessLogEntry":
        ret = super().create(**kwargs)
        if not kwargs.get("task_func", ""):
            kwargs["task_func"] = random.choice(list(BackgroundManager().get_all_tasks().values()))
        if kwargs.get("task_func"):
            kwargs["task_name"] = kwargs["task_func"].split(".")[-1]

        return ret
