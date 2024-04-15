from rest_framework_extensions.routers import ExtendedDefaultRouter

from . import views
from .trigger import TriggerViewSet

router = ExtendedDefaultRouter()
router.register(r"trigger", TriggerViewSet, basename="trigger")
u = router.register(r"user", views.UserViewSet)


o = router.register(r"organization", views.OrganizationViewSet)
o.register(
    r"channels",
    views.ChannelViewSet,
    basename="org-channel",
    parents_query_lookups=[
        "organization__slug",
    ],
)
#
p = o.register(r"projects", views.ProjectViewSet, basename="project", parents_query_lookups=["organization__slug"])

p.register(
    r"channels",
    views.ChannelViewSet,
    basename="prj-channel",
    parents_query_lookups=[
        "application__project__organization__slug",
        "application__project__slug",
        "application__slug",
    ],
)
a = p.register(
    r"applications",
    views.ApplicationViewSet,
    basename="application",
    parents_query_lookups=["project__organization__slug", "project__slug"],
)
e = a.register(
    r"events",
    views.EventViewSet,
    basename="event",
    parents_query_lookups=[
        "application__project__organization__slug",
        "application__project__slug",
        "application__slug",
    ],
)
#
# e.register(
#     r"channels",
#     views.ChannelViewSet,
#     basename="evt-channel",
#     parents_query_lookups=[
#         "application__project__organization__slug",
#         "application__project__slug",
#         # "channels__application__slug",
#     ],
# )
