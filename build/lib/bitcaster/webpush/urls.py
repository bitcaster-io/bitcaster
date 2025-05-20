from django.urls import path

from .views import ConfirmView, DataView, ServiceWorker, SubscribeView, UnSubscribeView

app_name = "webpush"

urlpatterns = [
    path("confirm/<str:secret>/", ConfirmView.as_view(), name="ask"),
    path("confirm/<str:secret>/data/", DataView.as_view(), name="data"),
    path("unsubscribe/<str:secret>/", UnSubscribeView.as_view(), name="unsubscribe"),
    path("subscribe/<str:secret>/", SubscribeView.as_view(), name="subscribe"),
    path("<slug:application>/sw.js", ServiceWorker.as_view(), name="service_worker"),
]
