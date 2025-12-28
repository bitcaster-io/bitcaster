import json
from typing import Any

from django.db import models
from django.db.models.functions import TruncHour
from unfold.components import BaseComponent, register_component

from bitcaster.cache.manager import CacheManager
from bitcaster.models import Occurrence

from ..utils import get_dates


@register_component
class CurrentChartComponent(BaseComponent):
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        cm = CacheManager(self.request)
        if not (chart_data := cm.retrieve("dashboard:cache:CurrentChartComponent")):  # FIX: Changed cache key
            # Get the start and end date for the last 30 days
            start_date, end_date = get_dates()

            # Query occurrences for today (end_date), grouped by hour and status
            occurrences_by_hour = (
                Occurrence.objects.filter(timestamp__date=end_date)
                .annotate(hour=TruncHour("timestamp"))
                .values("hour", "status")
                .annotate(count=models.Count("id"))
                .order_by("hour", "status")
            )

            # Create a dictionary to hold the data
            data_map = {}
            for item in occurrences_by_hour:
                hour = item["hour"].strftime("%H")
                status = item["status"]
                data_map[(hour, status)] = item["count"]

            # Generate labels for 24 hours
            labels = [f"{i:02d}" for i in range(24)]

            datasets = []
            colors = {
                Occurrence.Status.PROCESSED: "var(--color-green-500)",
                Occurrence.Status.FAILED: "var(--color-red-500)",
                Occurrence.Status.NEW: "var(--color-gray-500)",
            }

            for status in Occurrence.Status:
                data = [data_map.get((label, status.value), 0) for label in labels]
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
            cm.store("dashboard:cache:CurrentChartComponent", chart_data)  # FIX: Changed cache key
        context.update(chart_data)

        return context
