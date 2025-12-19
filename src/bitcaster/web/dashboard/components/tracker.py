from typing import Any

from django.db.models import Count
from unfold.components import BaseComponent, register_component

from bitcaster.cache.manager import CacheManager
from bitcaster.models import Occurrence
from bitcaster.web.dashboard.utils import get_dates


@register_component
class ErrorTrackerComponent(BaseComponent):
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        start_date, end_date = get_dates()
        cm = CacheManager(self.request)
        if not (data := cm.retrieve("dashboard:tracker")):
            data = []
            colors = {
                Occurrence.Status.NEW: "bg-gray-700",
                Occurrence.Status.PROCESSED: "bg-green-700",
                Occurrence.Status.FAILED: "bg-red-700",
            }
            for c in (
                Occurrence.objects.filter(timestamp__range=(start_date, end_date))
                .values("status")
                .annotate(count=Count("id"))
            ):
                data.extend([{"color": colors[c["status"]], "tooltip": c["count"]} for x in range(c["count"])])
            cm.store("dashboard:tracker", data)
        context.update({"data": data})
        return context
