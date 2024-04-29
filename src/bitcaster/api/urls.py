from django.urls import include, path

from .router import router
from .system import PingView

app_name = "api"


urlpatterns = [
    path("system/ping/", PingView.as_view(), name="system-ping"),
    path("", include(router.urls)),
]
