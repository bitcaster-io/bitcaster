import re

from django.conf import settings
from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("admin/logout/", views.LogoutView.as_view(), name="logout"),
    path("healthcheck/", views.HealthCheckView.as_view(), name="healthcheck"),
    re_path(r"^%s(?P<path>.*)$" % re.escape(settings.MEDIA_URL.lstrip("/")), views.MediaView.as_view()),
]
