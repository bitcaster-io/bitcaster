import json
from datetime import timedelta
from typing import Any

from django.db import models
from django.db.models.functions import TruncDay
from unfold.components import BaseComponent, register_component

from bitcaster.models import Occurrence

from ..cache import CacheManager
from ..utils import get_dates


@register_component
class OccurrenceChartComponent(BaseComponent):
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        cm = CacheManager(self.request)
        if not (chart_data := cm.retrieve("dashboard:cache:OccurrenceChartComponent")):
            # Get the start and end date for the last 30 days
            start_date, end_date = get_dates()

            # Query occurrences and group by day
            occurrences_by_day = (
                Occurrence.objects.filter(timestamp__range=(start_date, end_date))
                .annotate(day=TruncDay("timestamp"))
                .values("day")
                .annotate(count=models.Count("id"))
                .order_by("day")
            )

            # Create a dictionary to hold the data for each day
            data_map = {item["day"].strftime("%Y-%m-%d"): item["count"] for item in occurrences_by_day}

            # Generate all dates from start_date to end_date
            all_dates = [start_date + timedelta(days=i) for i in range(31)]
            labels = [date.strftime("%b %d") for date in all_dates]
            data_keys = [date.strftime("%Y-%m-%d") for date in all_dates]
            data = [data_map.get(key, 0) for key in data_keys]
            chart_data = {
                "height": 220,
                "data": json.dumps(
                    {
                        "labels": labels,
                        "datasets": [
                            {
                                "label": "Occurrences",
                                "data": data,
                                "backgroundColor": "var(--color-primary-700)",
                                "type": "bar",
                            },
                        ],
                    }
                ),
            }
            cm.store("dashboard:cache:OccurrenceChartComponent", chart_data)
        context.update(chart_data)

        return context
