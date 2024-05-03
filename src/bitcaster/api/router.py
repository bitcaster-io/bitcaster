from rest_framework_extensions.routers import ExtendedDefaultRouter

from .trigger import TriggerViewSet


class R(ExtendedDefaultRouter):
    include_format_suffixes = False


router = R()

router.register("trigger", TriggerViewSet, basename="trigger")
# # u = router.register("user", views.UserViewSet)
#
# org = router.register(r"o", views.OrganizationViewSet)
# org.register("c", views.ChannelViewSet, basename="org-channel", parents_query_lookups=["organization__slug"])
# prj = org.register(r"p", views.ProjectViewSet, basename="org-project", parents_query_lookups=["organization__slug"])
#
# # org.register(
# #     r"c",
# #     views.ChannelViewSet,
# #     basename="org-channel",
# #     parents_query_lookups=[
# #         "application__project__organization__slug",
# #     ],
# # )
# app = prj.register(
#     "a",
#     views.ApplicationViewSet,
#     basename="prj-application",
#     parents_query_lookups=["project__organization__slug", "project__slug"],
# )
# prj_ch = prj.register(
#     "c",
#     views.ChannelViewSet,
#     basename="prj-channel",
#     parents_query_lookups=["project__organization__slug", "project__slug"],
# )
# evt = app.register(
#     "e",
#     views.EventViewSet,
#     basename="app-event",
#     parents_query_lookups=[
#         "application__project__organization__slug",
#         "application__project__slug",
#         "application__slug",
#     ],
# )
# # ev_ch = evt.register(
# #     "ch",
# #     views.EventViewSet,
# #     basename="app-channel",
# #     parents_query_lookups=[
# #         "application__project__organization__slug",
# #         "application__project__slug",
# #         "application__slug",
# #     ],
# # )
