import debug_toolbar
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("", include("bitcaster.web.urls")),
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/schema/raw/", SpectacularAPIView.as_view(), name="schema"),
    path("api/", include("bitcaster.api.urls", namespace="api")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("adminactions/", include("adminactions.urls")),
    path("tinymce/", include("tinymce.urls")),
    path("social/", include("social_django.urls", namespace="social")),
    path(r"__debug__/", include(debug_toolbar.urls)),
]
