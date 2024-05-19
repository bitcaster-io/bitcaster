from django.urls import path
from rest_framework_extensions.routers import ExtendedDefaultRouter

from .distribution_list import DistributionView
from .event import EventList, EventTrigger
from .org import OrgView
from .system import PingView
from .user import UserView

app_name = "api"


router = ExtendedDefaultRouter()

urlpatterns = [
    path("system/ping/", PingView.as_view(), name="system-ping"),
    #
    path("o/<slug:org>/", OrgView.as_view({"get": "retrieve"}), name="org"),
    #
    path("o/<slug:org>/u/<str:username>/address/", UserView.as_view({"get": "address", "post": "address"})),
    path("o/<slug:org>/u/<str:username>/", UserView.as_view({"put": "update"}), name="user-update"),
    path("o/<slug:org>/u/", UserView.as_view({"get": "get", "post": "post", "put": "update"}), name="user-list"),
    #
    path("o/<slug:org>/c/", OrgView.as_view({"get": "channels"}), name="org-channel-list"),
    #
    path("o/<slug:org>/p/<slug:prj>/d/<int:pk>/add/", DistributionView.as_view({"post": "add_recipient"})),
    path("o/<slug:org>/p/<slug:prj>/d/", DistributionView.as_view({"get": "list"}), name="distribution"),
    #
    path("o/<slug:org>/p/<slug:prj>/a/<slug:app>/e/", EventList.as_view(), name="event-list"),
    path("o/<slug:org>/p/<slug:prj>/a/<slug:app>/e/<slug:evt>/trigger/", EventTrigger.as_view(), name="event-trigger"),
]
