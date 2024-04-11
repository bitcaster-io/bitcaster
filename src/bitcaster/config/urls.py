import debug_toolbar
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("bitcaster.api.urls", namespace="api")),
    path(r"social/", include("social_django.urls", namespace="social")),
    path(r"accounts/", include("django.contrib.auth.urls")),
    path(r"adminactions/", include("adminactions.urls")),
    path(r"__debug__/", include(debug_toolbar.urls)),
]
