from rest_framework_extensions.routers import ExtendedDefaultRouter

from .trigger import EventViewSet, TriggerViewSet


class R(ExtendedDefaultRouter):
    include_format_suffixes = False


router = R()

router.register("events", EventViewSet, basename="events")
router.register("trigger", TriggerViewSet, basename="trigger")
