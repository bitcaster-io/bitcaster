from django.urls import path

from .views import UserConsoleDetailView, UserConsoleIndexView, UserConsoleUserPrefsView

app_name = "console"

urlpatterns = [
    path("", UserConsoleIndexView.as_view(), name="index"),
    path("<int:pk>/", UserConsoleDetailView.as_view(), name="detail"),
    path("prefs/", UserConsoleUserPrefsView.as_view(), name="prefs"),
]
