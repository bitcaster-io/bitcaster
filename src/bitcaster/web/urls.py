import re

from django.conf import settings
from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="home"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("admin/logout/", views.LogoutView.as_view(), name="logout"),
    path("attachment/download/<str:key>/", views.SafeAttachmentDownloadView.as_view(), name="safe_download"),
    path("healthcheck/", views.HealthCheckView.as_view(), name="healthcheck"),
    re_path(r"^%s(?P<path>.*)$" % re.escape(settings.MEDIA_URL.lstrip("/")), views.MediaView.as_view()),
]
