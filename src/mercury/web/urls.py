from django.urls import path

from .views import HomeView, LoginView, LogoutView

urlpatterns = [
    path(r'login/', LoginView.as_view(), name='login'),
    path(r'logout/', LogoutView.as_view(), name='logout'),
    path(r'', HomeView.as_view())
]
