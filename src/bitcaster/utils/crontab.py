from celery import schedules
from cron_descriptor import (
    FormatException,
    MissingFieldException,
    WrongArgumentException,
    get_description,
)
from django.utils.translation import gettext as _
from django_celery_beat.models import CrontabSchedule, cronexp


def human_readable(crontab: CrontabSchedule) -> str:
    try:
        ct = schedules.crontab(
            minute=crontab.minute,
            hour=crontab.hour,
            day_of_week=crontab.day_of_week,
            day_of_month=crontab.day_of_month,
            month_of_year=crontab.month_of_year,
        )
        if len(ct.day_of_week) == 7:
            day_of_week = _("Every day")
        else:
            day_of_week = cronexp(",".join(str(day) for day in ct.day_of_week))
    except ValueError:
        day_of_week = cronexp(crontab.day_of_week)

    cron_expression = (
        f"{cronexp(crontab.minute)} {cronexp(crontab.hour)}"
        f" {cronexp(crontab.day_of_month)} {cronexp(crontab.month_of_year)} {day_of_week}"
    )
    try:
        readable = get_description(cron_expression)
    except (MissingFieldException, FormatException, WrongArgumentException):
        return f"{cron_expression} {str(crontab.timezone)}"
    return f"{readable} {str(crontab.timezone)}"
