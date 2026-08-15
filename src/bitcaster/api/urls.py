from rest_framework_extensions.routers import ExtendedDefaultRouter

from django.urls import path

from .application import ApplicationView
from .attachments import AttachmentView
from .channel import ChannelView
from .distribution_list import DistributionMembersView, DistributionView
from .event import EventList, EventTrigger
from .org import OrgView
from .profile import UserProfileView
from .project import ProjectView
from .register import ApplicationRegisterView
from .subscription import NotificationSubscriptionView
from .system import LoginView, PingView
from .token import ClientTokenView
from .unregister import ApplicationUnregisterView
from .unsubscribe import ApplicationUnsubscribeView
from .user import UserView

app_name = "api"

router = ExtendedDefaultRouter()

urlpatterns = [
    path("login/", LoginView.as_view(), name="api-login"),
    path("system/ping/", PingView.as_view(), name="system-ping"),
    path("me/", UserProfileView.as_view({"get": "retrieve"}), name="user-profile"),
    path("me/messages/", UserProfileView.as_view({"get": "messages"}), name="user-profile-messages"),
    path("me/unseen/", UserProfileView.as_view({"get": "unseen"}), name="user-profile-unseen"),
    path("me/addresses/", UserProfileView.as_view({"get": "addresses"}), name="user-profile-addresses"),
    path("o/<slug:org>/", OrgView.as_view({"get": "retrieve"}), name="org"),
    path("o/<slug:org>/c/", ChannelView.as_view({"get": "list_for_org"}), name="org-channel-list"),
    path("o/<slug:org>/c/<int:pk>/", ChannelView.as_view({"get": "retrieve"}), name="channel-detail"),
    path(
        "o/<slug:org>/u/<str:username>/addresses/",
        UserView.as_view({"get": "list_address", "post": "add_address"}),
        name="user-addresses",
    ),
    path(
        "o/<slug:org>/u/<str:username>/",
        UserView.as_view({"put": "update", "patch": "update", "get": "retrieve"}),
        name="user-update",
    ),
    path(
        "o/<slug:org>/u/<str:username>/messages/",
        UserView.as_view({"get": "list_messages"}),
        name="user-messages",
    ),
    path("o/<slug:org>/u/", UserView.as_view({"get": "list", "post": "create"}), name="user-list"),
    path("o/<slug:org>/p/", ProjectView.as_view({"get": "list"}), name="project-list"),
    path("o/<slug:org>/p/<slug:prj>/", ProjectView.as_view({"get": "retrieve"}), name="project-detail"),
    path("o/<slug:org>/p/<slug:prj>/a/", ApplicationView.as_view({"get": "list"}), name="project-application-list"),
    path(
        "o/<slug:org>/p/<slug:prj>/a/<slug:app>/",
        ApplicationView.as_view({"get": "retrieve"}),
        name="application-detail",
    ),
    path("o/<slug:org>/p/<slug:prj>/c/", ChannelView.as_view({"get": "list_for_project"}), name="project-channel-list"),
    path("o/<slug:org>/p/<slug:prj>/c/<int:pk>/", ChannelView.as_view({"get": "retrieve"}), name="channel-retrieve"),
    path(
        "o/<slug:org>/p/<slug:prj>/d/<int:pk>/m/", DistributionMembersView.as_view({"get": "list"}), name="members-list"
    ),
    path("o/<slug:org>/p/<slug:prj>/d/<int:pk>/add/", DistributionView.as_view({"post": "add_recipient"})),
    path(
        "o/<slug:org>/p/<slug:prj>/d/<int:pk>/",
        DistributionView.as_view({"get": "retrieve"}),
        name="distribution-detail",
    ),
    path("o/<slug:org>/p/<slug:prj>/d/", DistributionView.as_view({"get": "list"}), name="distribution-list"),
    path("o/<slug:org>/p/<slug:prj>/a/<slug:app>/e/<slug:evt>/trigger/", EventTrigger.as_view(), name="event-trigger"),
    path("o/<slug:org>/p/<slug:prj>/a/<slug:app>/token/", ClientTokenView.as_view(), name="client-token"),
    path("o/<slug:org>/p/<slug:prj>/a/<slug:app>/e/", EventList.as_view(), name="events-list"),
    path("o/<slug:org>/p/<slug:prj>/a/<slug:app>/attachment/", AttachmentView.as_view(), name="attachment-upload"),
    path(
        "o/<slug:org>/p/<slug:prj>/a/<slug:app>/attachment/<slug:correlation_id>/",
        AttachmentView.as_view(),
        name="attachment-upload-with-correlation-id",
    ),
    path(
        "o/<slug:org>/p/<slug:prj>/a/<slug:app>/register/",
        ApplicationRegisterView.as_view(),
        name="application-register",
    ),
    path(
        "o/<slug:org>/p/<slug:prj>/a/<slug:app>/unregister/<str:username>/",
        ApplicationUnregisterView.as_view(),
        name="application-unregister",
    ),
    path(
        "o/<slug:org>/p/<slug:prj>/a/<slug:app>/unsubscribe/<str:username>/",
        ApplicationUnsubscribeView.as_view(),
        name="application-unsubscribe",
    ),
    path(
        "o/<slug:org>/p/<slug:prj>/a/<slug:app>/n/<int:notification_pk>/subscribe/",
        NotificationSubscriptionView.as_view(),
        name="notification-subscribe",
    ),
]
