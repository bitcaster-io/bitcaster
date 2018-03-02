from django.urls import include, path
from django.views.generic import TemplateView

from mercury.web.views.setup import SetupView
from mercury.web.views.views import (ApplicationCreate,
                                     OrganizationCreate, SettingsView,)

from .views import (ApplicationDetail, ChannelList, EventList, LoginView,
                    LogoutView, MessageList, OrganizationDetail,
                    SubscriptionList, UserProfileView, UserRegister,
                    confirm_email,)

urlpatterns = [
    path(r'setup/', SetupView.as_view(), name='setup'),
    path(r'login/', LoginView.as_view(), name='login'),
    path(r'logout/', LogoutView.as_view(), name='logout'),
    path(r'settings/<str:section>/', SettingsView.as_view(), name='settings'),
    path(r'settings/', SettingsView.as_view(), name='settings'),

    path(r'', include('social_django.urls', namespace='social')),

    path(r'user/register/', UserRegister.as_view(), name='user-register'),
    path(r'org/add/', OrganizationCreate.as_view(), name='org-add'),
    path(r'<slug:org>/add/', ApplicationCreate.as_view(), name='application-add'),

    path(r'user/register/register-wait-email/<int:pk>/',
         TemplateView.as_view(template_name='bitcaster/registration/register_wait_email.html'),
         name='register-wait-email'),
    path(r'user/register/confirm-email/<int:pk>/<str:check>/',
         confirm_email, name='confirm-email'),
    path(r'user/profile/', UserProfileView.as_view(), name='user-profile'),

    path(r'new-user/', TemplateView.as_view(template_name='bitcaster/new-user.html')),
    path(r'new-association/', TemplateView.as_view(template_name='bitcaster/new-association.html')),

    path(r'terms/', TemplateView.as_view(template_name='bitcaster/legal/terms.html'), name='legal-terms'),
    path(r'privacy/', TemplateView.as_view(template_name='bitcaster/legal/privacy.html'), name='legal-privacy'),

    path(r'<slug:org>/', OrganizationDetail.as_view(), name='org-index'),

    path(r'<slug:org>/<slug:app>/', ApplicationDetail.as_view(), name='app-index'),

    path(r'<slug:org>/<slug:app>/subscriptions/',
         SubscriptionList.as_view(), name='app-subscriptions'),

    path(r'<slug:org>/<slug:app>/events/',
         EventList.as_view(), name='app-events'),

    path(r'<slug:org>/<slug:app>/channels/',
         ChannelList.as_view(), name='app-channels'),

    path(r'<slug:org>/<slug:app>/messages/',
         MessageList.as_view(), name='app-messages'),

    path(r'', TemplateView.as_view(template_name='bitcaster/index.html'),
         name='index'),

]
