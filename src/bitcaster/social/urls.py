from django.urls import path
from django.views.generic import TemplateView

app_name = "social"

urlpatterns = [
    path("nologin/", TemplateView.as_view(template_name="bitcaster/social/registration_error.html"), name="nologin"),
    path("nosigup/", TemplateView.as_view(template_name="bitcaster/social/registration_error.html"), name="nosigup"),
    path("noauth/", TemplateView.as_view(template_name="bitcaster/social/registration_error.html"), name="not-allowed"),
]
