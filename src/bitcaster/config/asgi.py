import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from ..chrome.auth import TokenAuthMiddleware
from ..chrome.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bitcaster.config.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(TokenAuthMiddleware(URLRouter(websocket_urlpatterns))),
    }
)
