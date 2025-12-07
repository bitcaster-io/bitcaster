import debug_toolbar
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from bitcaster.admin_site import ConsoleAdminSite

# The BitcasterAdminSite is set as the default in settings.py,
# so we can use admin.site directly. We only need to instantiate
# the secondary console site.
console = ConsoleAdminSite(name="console")
console.autodiscover()

urlpatterns = [
    path("", include("bitcaster.web.urls")),
    path("console/", include((console.get_urls(), "console"), namespace="console")),
    path("admin/", admin.site.urls),
    # path("console/", console.urls),
    path("webpush/", include("bitcaster.webpush.urls")),
    path("api/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/raw/", SpectacularAPIView.as_view(), name="schema"),
    path("api/", include("bitcaster.api.urls", namespace="api")),
    path("adminactions/", include("adminactions.urls")),
    path("tinymce/", include("tinymce.urls")),
    path("social/", include("social_django.urls", namespace="social")),
    path("select2/", include("django_select2.urls")),
    path(r"__debug__/", include(debug_toolbar.urls)),
]
