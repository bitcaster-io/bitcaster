from datetime import datetime, timedelta

from django.utils import timezone

HOUR = 60 * 60


def get_dates(days: int = 30) -> tuple[datetime, datetime]:
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date
