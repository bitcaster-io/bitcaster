from django.urls import re_path

from .consumers import ChromeConsumer

# The user-facing URL will be /chrome/<email>/
# The websocket connection should be ws/chrome/<email>/
websocket_urlpatterns = [
    re_path(r"^chrome/(?P<email>[\w._+-]+)/$", ChromeConsumer.as_asgi()),
]
