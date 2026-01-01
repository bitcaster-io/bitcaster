import json
from datetime import timedelta
from typing import Any

from django.db import models
from django.db.models.functions import TruncDay
from unfold.components import BaseComponent, register_component

from bitcaster.cache.manager import CacheManager
from bitcaster.models import Occurrence

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
                .values("day", "status")
                .annotate(count=models.Count("id"))
                .order_by("day", "status")
            )

            data_map = {}
            for item in occurrences_by_day:
                day_str = item["day"].strftime("%Y-%m-%d")
                status = item["status"]
                data_map[(day_str, status)] = item["count"]

            all_dates = [start_date + timedelta(days=i) for i in range(31)]
            labels = [date.strftime("%b %d") for date in all_dates]
            data_keys = [date.strftime("%Y-%m-%d") for date in all_dates]

            datasets = []
            colors = {
                Occurrence.Status.PROCESSED: "var(--color-green-500)",
                Occurrence.Status.FAILED: "var(--color-red-500)",
                Occurrence.Status.NEW: "var(--color-gray-500)",
            }
            for status in Occurrence.Status:
                data = [data_map.get((key, status.value), 0) for key in data_keys]
                datasets.append(
                    {
                        "label": str(status.label),
                        "data": data,
                        "backgroundColor": colors.get(status, "var(--color-gray-500)"),
                        "type": "bar",
                    }
                )
            chart_data = {
                "height": 220,
                "data": json.dumps({"labels": labels, "datasets": datasets}),
            }
            cm.store("dashboard:cache:OccurrenceChartComponent", chart_data)
        context.update(chart_data)

        return context
