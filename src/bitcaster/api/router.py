from rest_framework.routers import DefaultRouter
from rest_framework_extensions.routers import NestedRouterMixin

from . import views


class SimpleRouterWithNesting(NestedRouterMixin, DefaultRouter):
    pass


router = SimpleRouterWithNesting()


office = router.register(r"organization", views.OrganizationViewSet)
