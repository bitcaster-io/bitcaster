import debug_toolbar
from django.contrib import admin
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("", include("bitcaster.web.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("pwa/", include("bitcaster.pwa.urls")),
    path("admin/", admin.site.urls),
    path("console/", include("bitcaster.console.urls", namespace="console")),
    path("chaining/", include("smart_selects.urls")),
    path("webpush/", include("bitcaster.webpush.urls")),
    path("api/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/raw/", SpectacularAPIView.as_view(), name="schema"),
    path("api/", include("bitcaster.api.urls", namespace="api")),
    path("adminactions/", include("adminactions.urls")),
    path("tinymce/", include("tinymce.urls")),
    path("social/", include("allauth.urls")),
    path("mfa/", include("allauth.mfa.urls")),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path(r"__debug__/", include(debug_toolbar.urls)),
]
