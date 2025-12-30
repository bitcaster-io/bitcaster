import pytest

from bitcaster.models import Task


@pytest.mark.django_db
def test_task_scheduling_interval():
    task = Task.objects.create(
        name="TestIntervalTask",
        func="some.module.some_function",
        trigger=Task.TriggerOption.INTERVAL,
        trigger_config={"weeks": 1, "days": 2, "hours": 3, "minutes": 4, "seconds": 5},
    )
    expected_output = "Every 1 week, 2 days, 3 hours, 4 minutes, 5 seconds"
    assert task.scheduling() == expected_output

    task_singular = Task.objects.create(
        name="TestIntervalTaskSingular",
        func="some.module.some_function",
        trigger=Task.TriggerOption.INTERVAL,
        trigger_config={
            "days": 1,
            "hours": 1,
            "minutes": 1,
        },
    )
    expected_output_singular = "Every 1 day, 1 hour, 1 minute"
    assert task_singular.scheduling() == expected_output_singular


@pytest.mark.django_db
def test_task_scheduling_cron():
    task = Task.objects.create(
        name="TestCronTask",
        func="some.module.some_function",
        trigger=Task.TriggerOption.CRON,
        trigger_config={
            "minute": "0",
            "hour": "10",
            "day_of_week": "mon,tue",
            "month": "1",
        },
    )
    expected_output = "At 10:00 AM, only on Monday and Tuesday, only in January"
    assert task.scheduling() == expected_output

    task_all_wildcards = Task.objects.create(
        name="TestCronTaskAllWildcards",
        func="some.module.some_function",
        trigger=Task.TriggerOption.CRON,
        trigger_config={},  # All wildcards
    )
    expected_output_all_wildcards = "Every minute"
    assert task_all_wildcards.scheduling() == expected_output_all_wildcards

    task_every_hour = Task.objects.create(
        name="TestCronTaskEveryHour",
        func="some.module.some_function",
        trigger=Task.TriggerOption.CRON,
        trigger_config={
            "minute": "0",
        },
    )
    expected_output_every_hour = "Every hour"
    assert task_every_hour.scheduling() == expected_output_every_hour
