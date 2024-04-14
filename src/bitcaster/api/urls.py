from django.urls import include, path

from .router import router

app_name = "api"


urlpatterns = [
    path("", include(router.urls)),
    # path("schema/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    # path("schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # path("schema/raw/", SpectacularAPIView.as_view(), name="schema"),
    # path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # path("sentry-debug", trigger_error),
]
