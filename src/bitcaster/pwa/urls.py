from django.urls import path
from django.views.generic import TemplateView

from .views import (
    # MobileRegisterView,
    PwaDetailView,
    PwaIndexView,
    PwaLoginView,
    PwaLogoutView,
    PwaPrefsView,
    PwaServiceWorker,
    manifest,
    offline,
)

app_name = "pwa"

urlpatterns = [
    path("", PwaIndexView.as_view(), name="index"),
    path("login/", PwaLoginView.as_view(), name="login"),
    path("logout/", PwaLogoutView.as_view(), name="logout"),
    path("<int:pk>/", PwaDetailView.as_view(), name="detail"),
    path("prefs/", PwaPrefsView.as_view(), name="prefs"),
    path("manifest.json", manifest, name="manifest"),
    path("serviceworker.js", PwaServiceWorker.as_view(), name="serviceworker"),
    path("offline/", offline, name="offline"),
    path("installed/", TemplateView.as_view(template_name="pwa/installed.html"), name="installed"),
    path("about/", TemplateView.as_view(template_name="pwa/about.html"), name="about"),
]
