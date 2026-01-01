import factory

from bitcaster.models import Task

from .base import AutoRegisterModelFactory


class TaskFactory(AutoRegisterModelFactory[Task]):
    name = factory.Sequence(lambda n: "task%s" % n)
    func = "bitcaster.runner.tasks.scan_occurrences"
    trigger = "interval"
    trigger_config = {"minutes": 1}

    class Meta:
        model = Task
        django_get_or_create = ("name",)
