from django.urls import path

from .system import PingView
from .views import EventList, EventTrigger

app_name = "api"


urlpatterns = [
    path("system/ping/", PingView.as_view(), name="system-ping"),
    path("o/<slug:org>/p/<slug:prj>/a/<slug:app>/e/", EventList.as_view(), name="event-list"),
    path("o/<slug:org>/p/<slug:prj>/a/<slug:app>/e/<slug:evt>/trigger/", EventTrigger.as_view(), name="event-trigger"),
]
