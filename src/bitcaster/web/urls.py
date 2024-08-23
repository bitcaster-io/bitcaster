import re

from django.conf import settings
from django.urls import path, re_path
from flags.urls import flagged_path

from . import views, wizards
from .views import MediaView

urlpatterns = [
    path("", views.index, name="home"),
    # path("lock/", wizards.LockingWizard.as_view(), name="locking"),
    flagged_path("BETA_PREVIEW_LOCKING", "lock/", wizards.LockingWizard.as_view(), name="locking", state=True),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("admin/logout/", views.LogoutView.as_view(), name="logout"),
    path("healthcheck/", views.HealthCheckView.as_view(), name="healthcheck"),
    re_path(r"^%s(?P<path>.*)$" % re.escape(settings.MEDIA_URL.lstrip("/")), MediaView.as_view()),
]
