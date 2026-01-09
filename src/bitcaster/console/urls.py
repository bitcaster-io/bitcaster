from django.urls import path

from .views import ConsoleDetailView, ConsoleIndexView

app_name = "console"

urlpatterns = [
    path("", ConsoleIndexView.as_view(), name="index"),
    path("<int:pk>/", ConsoleDetailView.as_view(), name="detail"),
]
