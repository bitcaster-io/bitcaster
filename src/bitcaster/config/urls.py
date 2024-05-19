import debug_toolbar
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("", include("bitcaster.web.urls")),
    path("admin/", admin.site.urls),
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
