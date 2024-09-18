import factory
from django.utils import timezone
from django_celery_beat.models import (
    SOLAR_SCHEDULES,
    ClockedSchedule,
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
    SolarSchedule,
)
from factory.fuzzy import FuzzyChoice

from .base import AutoRegisterModelFactory


class IntervalScheduleFactory(AutoRegisterModelFactory[IntervalSchedule]):
    every = 1
    period = IntervalSchedule.HOURS

    class Meta:
        model = IntervalSchedule


class SolarScheduleFactory(AutoRegisterModelFactory[SolarSchedule]):
    event = FuzzyChoice([x[0] for x in SOLAR_SCHEDULES])

    latitude = 10.1
    longitude = 10.1

    class Meta:
        model = SolarSchedule


class ClockedScheduleFactory(AutoRegisterModelFactory[ClockedSchedule]):
    clocked_time = timezone.now()

    class Meta:
        model = ClockedSchedule


class CrontabScheduleFactory(AutoRegisterModelFactory[CrontabSchedule]):
    class Meta:
        model = CrontabSchedule


class PeriodicTaskFactory(AutoRegisterModelFactory[PeriodicTask]):
    name = factory.Sequence(lambda n: "PeriodicTask%03d" % n)
    # interval = factory.SubFactory(IntervalScheduleFactory)
    crontab = factory.SubFactory(CrontabScheduleFactory)
    task = "bitcaster.tasks.purge_occurrences"

    class Meta:
        model = PeriodicTask
