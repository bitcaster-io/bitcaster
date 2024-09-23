from typing import Any
from unittest import mock

import pytest
from cron_descriptor.Exception import (
    FormatException,
    MissingFieldException,
    WrongArgumentException,
)
from django_celery_beat.models import CrontabSchedule
from testutils.factories.django_celery_beat import CrontabScheduleFactory

from bitcaster.utils.crontab import human_readable


@pytest.fixture
def crontabschedule(db: Any) -> CrontabSchedule:
    return CrontabScheduleFactory()


@pytest.mark.parametrize("crontab", [CrontabScheduleFactory.build(), CrontabScheduleFactory.build(day_of_week="1,2,3")])
def test_human_readable(crontab: CrontabSchedule) -> None:
    assert human_readable(crontab)


@pytest.mark.parametrize("crontab", [CrontabScheduleFactory.build(minute="aa", day_of_week="1")])
def test_human_readable_if_errors(crontab: CrontabSchedule) -> None:
    assert human_readable(crontab)


@pytest.mark.parametrize("exc", [MissingFieldException, FormatException, WrongArgumentException])
def test_human_readable_if_exception(exc: type[Exception], crontabschedule: CrontabSchedule) -> None:
    with mock.patch("bitcaster.utils.crontab.get_description", side_effect=exc("")):
        assert human_readable(crontabschedule) == "* * * * Every day UTC"
