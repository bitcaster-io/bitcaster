from typing import TYPE_CHECKING, Any

from constance import config

from django.core.paginator import Paginator
from django.http import HttpRequest

if TYPE_CHECKING:
    from django.core.paginator import Page

    from bitcaster.models import EventSimulation

DELIVERY_SELECT_RELATED = (
    "assignment__address__user",
    "assignment__channel",
    "notification",
    "message_template",
)


def simulation_page(simulation: "EventSimulation", request: HttpRequest) -> "Page":
    queryset = simulation.deliveries.select_related(*DELIVERY_SELECT_RELATED)
    paginator = Paginator(queryset, config.EVENT_SIMULATION_PAGE_SIZE)
    return paginator.get_page(request.GET.get("page"))


def simulation_results_context(simulation: "EventSimulation", page: "Page") -> dict[str, Any]:
    data = simulation.data
    partial_more = 0
    if simulation.mode == "partial":
        partial_more = max(
            0,
            data.get("recipients_count", 0) - data.get("rendered_count", 0) - data.get("missing_template_count", 0),
        )
    return {
        "simulation": simulation,
        "mode": simulation.mode,
        "page_obj": page,
        "missing_deliveries": [d for d in page.object_list if d.missing_template],
        "partial_more": partial_more,
    }
