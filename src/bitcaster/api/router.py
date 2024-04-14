from rest_framework.routers import DefaultRouter
from rest_framework_extensions.routers import NestedRouterMixin

from . import views
from .trigger import TriggerViewSet


class SimpleRouterWithNesting(NestedRouterMixin, DefaultRouter):
    pass


router = SimpleRouterWithNesting()


o = router.register(r"organization", views.OrganizationViewSet)
u = router.register(r"user", views.UserViewSet)
router.register(r"trigger", TriggerViewSet, basename="trigger")

p = o.register(r"projects", views.ProjectViewSet, basename="project", parents_query_lookups=["organization__slug"])

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

e = p.register(
    r"channels",
    views.ChannelViewSet,
    basename="channel",
    parents_query_lookups=[
        "application__project__organization__slug",
        "application__project__slug",
        "application__slug",
    ],
)
#
