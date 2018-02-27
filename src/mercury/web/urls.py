from django.urls import path

from .views import (ApplicationDetail, HomeView, LoginView,
                    LogoutView, SubscriptionList,)

urlpatterns = [
    path(r'login/', LoginView.as_view(), name='login'),
    path(r'logout/', LogoutView.as_view(), name='logout'),
    path(r'app/<int:pk>/', ApplicationDetail.as_view(), name='app-index'),
    path(r'subscriptions/', SubscriptionList.as_view(), name='user-subscriptions'),
    path(r'', HomeView.as_view())
]
