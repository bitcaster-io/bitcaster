from django.urls import include, path
from django.views.generic import TemplateView

from mercury.web.views.register import confirm_email

from .views import (ApplicationCreate, ApplicationDetail, ChannelList,
                    EventList, IndexView, LoginView, LogoutView, MessageList,
                    OrganizationApplications, OrganizationChannels,
                    OrganizationCreate, OrganizationDetail, OrganizationMembers,
                    OrganizationUpdate, SettingsChannelView, SettingsEmailView,
                    SettingsOAuthView, SettingsView, SetupView,
                    SubscriptionList, UserProfileView, UserRegister,)

# from mercury.web.views.settings import (SettingsChannelView, SettingsEmailView,
#                                         SettingsOAuthView, SettingsView,)
# from mercury.web.views.setup import SetupView
# from mercury.web.views.views import (IndexView,
#                                      OrganizationCreate, )
# from mercury.web.views.application import ApplicationCreate


urlpatterns = [
    path(r'setup/', SetupView.as_view(), name='setup'),
    path(r'login/', LoginView.as_view(), name='login'),
    path(r'logout/', LogoutView.as_view(), name='logout'),
    path(r'settings/', SettingsView.as_view(), name='settings'),
    path(r'settings/email/', SettingsEmailView.as_view(), name='settings-email'),
    path(r'settings/oauth/', SettingsOAuthView.as_view(), name='settings-oauth'),
    path(r'settings/channel/', SettingsChannelView.as_view(), name='settings-channels'),

    path(r'', include('social_django.urls', namespace='social')),

    path(r'user/register/', UserRegister.as_view(), name='user-register'),
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

    path(r'org/add/', OrganizationCreate.as_view(), name='org-add'),
    path(r'<slug:org>/details/', OrganizationDetail.as_view(), name='org-index'),
    path(r'<slug:org>/update/', OrganizationUpdate.as_view(), name='org-config'),
    path(r'<slug:org>/members/', OrganizationMembers.as_view(), name='org-members'),
    path(r'<slug:org>/channels/', OrganizationChannels.as_view(), name='org-channels'),
    path(r'<slug:org>/applications/', OrganizationApplications.as_view(), name='org-applications'),

    path(r'<slug:org>/<slug:app>/',
         ApplicationDetail.as_view(), name='app-index'),

    path(r'<slug:org>/<slug:app>/subscriptions/',
         SubscriptionList.as_view(), name='app-subscriptions'),

    path(r'<slug:org>/<slug:app>/events/',
         EventList.as_view(), name='app-events'),

    path(r'<slug:org>/<slug:app>/channels/',
         ChannelList.as_view(), name='app-channels'),

    path(r'<slug:org>/<slug:app>/messages/',
         MessageList.as_view(), name='app-messages'),

    path(r'', IndexView.as_view(),
         name='index'),

]
