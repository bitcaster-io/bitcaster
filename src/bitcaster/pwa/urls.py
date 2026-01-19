from django.urls import path

from .views import (  # acknowledge,; assetlinks,
    MobileRegisterView,
    PwaServiceWorker,
    manifest,
    offline, MobileView,
)

urlpatterns = [
    path("<str:secret>/", MobileView.as_view(), name="pwa-home"),
    path("register/", MobileRegisterView.as_view(), name="pwa-register"),
    path("<str:secret>/manifest.json", manifest, name="pwa-manifest"),
    path("serviceworker.js", PwaServiceWorker.as_view(), name="serviceworker"),
    path("offline/", offline, name="pwa-offline"),
]
