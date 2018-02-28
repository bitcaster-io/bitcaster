from django.urls import include, path
from django.views.generic import TemplateView

from .views import (ApplicationDetail, LoginView, LogoutView,
                    MercuryTemplateView, SubscriptionList,
                    UserProfile, UserRegister,)

urlpatterns = [
    path(r'login/', LoginView.as_view(), name='login'),
    path(r'logout/', LogoutView.as_view(), name='logout'),
    path(r'app/<int:pk>/', ApplicationDetail.as_view(), name='app-index'),
    path(r'subscriptions/', SubscriptionList.as_view(), name='user-subscriptions'),


    path(r'user/register/', UserRegister.as_view(), name='user-register'),
    path(r'user/profile/', UserProfile.as_view(), name='user-profile'),




    path(r'new-user/', TemplateView.as_view(template_name='bitcaster/new-user.html')),
    path(r'new-association/', TemplateView.as_view(template_name='bitcaster/new-association.html')),

    path(r'', include('social_django.urls', namespace='social')),
    path(r'home/',
         MercuryTemplateView.as_view(template_name='bitcaster/home.html'),
         name='home'),
    path(r'', TemplateView.as_view(template_name='bitcaster/index.html'),
         name='index'),

]
