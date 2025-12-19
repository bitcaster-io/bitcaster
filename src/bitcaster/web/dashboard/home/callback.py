from typing import TYPE_CHECKING, Any

from django.db.models import Count

from bitcaster.cache.manager import CacheManager
from bitcaster.models import Occurrence

from ..utils import get_dates

if TYPE_CHECKING:
    from django.http import HttpRequest


def dashboard_callback(request: "HttpRequest", context: dict[str, Any]) -> dict[str, Any]:
    start_date, end_date = get_dates()
    cm = CacheManager(request)
    if not (cards := cm.retrieve("dashboard:cards")):
        cards = {"TOTAL": {"title": "Total", "metric": 0}}
        cards.update({e[0]: {"title": e[1], "metric": 0} for e in Occurrence.Status.choices})
        total = 0

        for c in (
            Occurrence.objects.filter(timestamp__range=(start_date, end_date))
            .values("status")
            .annotate(count=Count("id"))
        ):
            cards[c["status"]]["metric"] = c["count"]
            total += c["count"]

        cards["TOTAL"]["metric"] = total
        cm.store("dashboard:cards", cards)

    context.update(
        {
            "cards": cards.values(),
        }
    )
    return context
