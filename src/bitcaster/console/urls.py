from django.urls import path

from .views import ConsoleDetailView, ConsoleIndexView, ConsoleUserPrefsView

app_name = "console"

urlpatterns = [
    path("", ConsoleIndexView.as_view(), name="index"),
    path("<int:pk>/", ConsoleDetailView.as_view(), name="detail"),
    path("prefs/", ConsoleUserPrefsView.as_view(), name="prefs"),
]
