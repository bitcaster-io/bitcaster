from django.urls import path
from rest_framework_extensions.routers import ExtendedDefaultRouter

from .application import ApplicationView
from .channel import ChannelView
from .distribution_list import DistributionMembersView, DistributionView
from .event import EventList, EventTrigger
from .org import OrgView
from .project import ProjectView
from .system import PingView
from .user import UserView

app_name = "api"


router = ExtendedDefaultRouter()

urlpatterns = [
    path("system/ping/", PingView.as_view(), name="system-ping"),
    path("o/<slug:org>/", OrgView.as_view({"get": "retrieve"}), name="org"),
    path("o/<slug:org>/c/", ChannelView.as_view({"get": "list_for_org"}), name="org-channel-list"),
    path("o/<slug:org>/u/<str:username>/address/", UserView.as_view({"get": "list_address", "post": "add_address"})),
    path("o/<slug:org>/u/<str:username>/", UserView.as_view({"put": "update"}), name="user-update"),
    path("o/<slug:org>/u/", UserView.as_view({"get": "get", "post": "post"}), name="user-list"),
    path("o/<slug:org>/p/", ProjectView.as_view({"get": "list"}), name="project-list"),
    path("o/<slug:org>/p/<slug:prj>/", ProjectView.as_view({"get": "retrieve"}), name="project-detail"),
    path("o/<slug:org>/p/<slug:prj>/a/", ApplicationView.as_view({"get": "list"}), name="project-application-list"),
    path("o/<slug:org>/p/<slug:prj>/c/", ChannelView.as_view({"get": "list_for_project"}), name="project-channel-list"),
    path(
        "o/<slug:org>/p/<slug:prj>/d/<int:pk>/m/", DistributionMembersView.as_view({"get": "list"}), name="members-list"
    ),
    path("o/<slug:org>/p/<slug:prj>/d/<int:pk>/add/", DistributionView.as_view({"post": "add_recipient"})),
    path("o/<slug:org>/p/<slug:prj>/d/<int:pk>/", DistributionView.as_view({"get": "list"}), name="distribution-list"),
    path("o/<slug:org>/p/<slug:prj>/d/", DistributionView.as_view({"get": "list"}), name="distribution-list"),
    path("o/<slug:org>/p/<slug:prj>/a/<slug:app>/e/<slug:evt>/trigger/", EventTrigger.as_view(), name="event-trigger"),
    path("o/<slug:org>/p/<slug:prj>/a/<slug:app>/e/", EventList.as_view(), name="events-list"),
]
