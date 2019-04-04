import logging

from django.conf.urls import include, url
from rest_framework_nested.routers import DefaultRouter, NestedSimpleRouter

from bitcaster.api.endpoints import ApplicationViewSet, EventViewSet

# from bitcaster.api.endpoints import (ApplicationViewSet, ChannelViewSet,
#                                      DispatcherViewSet, EventViewSet,
#                                      MessageViewSet, SubscriptionViewSet,
#                                      TimezoneViewSet, UserViewSet,)
# from bitcaster.api.endpoints.languages import LanguageViewSet


logger = logging.getLogger(__name__)

app_name = 'api'


class R(DefaultRouter):
    include_format_suffixes = False


router = R()
# router.register(r'languages', LanguageViewSet, base_name='language')
# router.register(r'timezones', TimezoneViewSet, base_name='timezone')
# router.register(r'users', UserViewSet)
router.register(r'applications', ApplicationViewSet)
# router.register(r'dispatchers', DispatcherViewSet, base_name='dispatcher')
# router.register(r'subscriptions', SubscriptionViewSet)

# router.register(r'channels', ChannelViewSet)
# router.register(r'messages', MessageViewSet)


# user = NestedSimpleRouter(router, r'users', lookup='user')
# user.register(r'subscriptions', SubscriptionViewSet, base_name='user-subscription')
# user.register(r'applications', ApplicationViewSet, base_name='user-application')

app = NestedSimpleRouter(router, r'applications', lookup='application')
app.register(r'events', EventViewSet, basename='application-event')
# app.register(r'channels', ChannelViewSet, base_name='application-channel')
# app.register(r'messages', MessageViewSet, base_name='application-message')

urlpatterns = (
    url(r'^', include(router.urls)),
    url(r'^', include(app.urls)),
    # url(r'^', include(user.urls)),
)
#
# urlpatterns = router.urls
