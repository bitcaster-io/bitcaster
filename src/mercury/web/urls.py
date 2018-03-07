from django.urls import include, path
from django.views.generic import TemplateView

from .views import (ApplicationCreate, ApplicationDetail, ChannelList,
                    EventList, IndexView, InviteAccept, InviteDelete,
                    InviteSend, LoginView, LogoutView, MessageList,
                    OrganizationApplications, OrganizationChannels,
                    OrganizationCreate, OrganizationDetail, OrganizationInvite,
                    OrganizationMembers, OrganizationUpdate,
                    SettingsChannelView, SettingsEmailView, SettingsOAuthView,
                    SettingsView, SetupView, SubscriptionList,
                    SystemChannelCreateWizard, UserProfileView, UserRegister,
                    UserWelcomeView, WorkInProgressView, confirm_email,)

urlpatterns = [
    path('setup/', SetupView.as_view(), name='setup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('settings/', SettingsView.as_view(), name='settings'),
    path('settings/email/', SettingsEmailView.as_view(), name='settings-email'),
    path('settings/oauth/', SettingsOAuthView.as_view(), name='settings-oauth'),
    path('settings/channel/', SettingsChannelView.as_view(), name='settings-channels'),
    path('settings/channel/add/', SystemChannelCreateWizard.as_view(), name='system-channel-create'),

    path('', include('social_django.urls', namespace='social')),

    path('user/register/', UserRegister.as_view(), name='user-register'),
    path('<slug:org>/add/', ApplicationCreate.as_view(), name='application-add'),

    path('user/register/register-wait-email/<int:pk>/',
         TemplateView.as_view(template_name='bitcaster/registration/register_wait_email.html'),
         name='register-wait-email'),
    path('user/register/confirm-email/<int:pk>/<str:check>/',
         confirm_email, name='confirm-email'),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),

    path('new-user/', TemplateView.as_view(template_name='bitcaster/new-user.html')),
    path('new-association/', TemplateView.as_view(template_name='bitcaster/new-association.html')),

    path('terms/', TemplateView.as_view(template_name='bitcaster/legal/terms.html'), name='legal-terms'),
    path('privacy/', TemplateView.as_view(template_name='bitcaster/legal/privacy.html'), name='legal-privacy'),

    path('org/add/', OrganizationCreate.as_view(), name='org-add'),

    path('<slug:org>/invite/accept/<int:pk>/<str:check>/', InviteAccept.as_view(),
         name='invitation-accept'),
    path('<slug:org>/invite/delete/<int:pk>/', InviteDelete.as_view(),
         name='invitation-delete'),
    path('<slug:org>/invite/send/<int:pk>/', InviteSend.as_view(),
         name='invitation-send'),
    path('<slug:org>/invite/', OrganizationInvite.as_view(),
         name='org-invite'),

    path('<slug:org>/user/<int:pk>/welcome/', UserWelcomeView.as_view(),
         name='user-welcome'),

    path('<slug:org>/details/', OrganizationDetail.as_view(), name='org-index'),
    path('<slug:org>/update/', OrganizationUpdate.as_view(), name='org-config'),
    path('<slug:org>/members/', OrganizationMembers.as_view(), name='org-members'),
    path('<slug:org>/channels/', OrganizationChannels.as_view(), name='org-channels'),
    path('<slug:org>/applications/', OrganizationApplications.as_view(), name='org-applications'),

    path('<slug:org>/<slug:app>/',
         ApplicationDetail.as_view(), name='app-index'),

    path('<slug:org>/<slug:app>/subscriptions/',
         SubscriptionList.as_view(), name='app-subscriptions'),

    path('<slug:org>/<slug:app>/events/',
         EventList.as_view(), name='app-events'),

    path('<slug:org>/<slug:app>/channels/',
         ChannelList.as_view(), name='app-channels'),

    path('<slug:org>/<slug:app>/messages/',
         MessageList.as_view(), name='app-messages'),

    path('', IndexView.as_view(),
         name='index'),

    path('wip/', WorkInProgressView.as_view(),
         name='wip'),

]
