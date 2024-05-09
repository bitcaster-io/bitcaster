import re

from django.conf import settings
from django.urls import path, re_path

from . import views
from .views import MediaView

urlpatterns = [
    path("", views.index, name="home"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("admin/logout/", views.LogoutView.as_view(), name="logout"),
    re_path(r"^%s(?P<path>.*)$" % re.escape(settings.MEDIA_URL.lstrip("/")), MediaView.as_view()),
]
