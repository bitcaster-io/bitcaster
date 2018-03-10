# line too long
# flake8: noqa: E501
from django.urls import include, path
from django.views.generic import TemplateView

from .views import (ApplicationChannelCreate, ApplicationChannelDeprecate,
                    ApplicationChannelRemove, ApplicationChannels,
                    ApplicationChannelToggle, ApplicationChannelUpdate,
                    ApplicationCreate, ApplicationDetail, EventList, IndexView,
                    InviteAccept, InviteDelete, InviteSend, LoginView,
                    LogoutView, MessageList, OrganizationApplications,
                    OrganizationChannelCreate, OrganizationChannelDeprecate,
                    OrganizationChannelRemove, OrganizationChannels,
                    OrganizationChannelToggle, OrganizationChannelUpdate,
                    OrganizationCreate, OrganizationDetail, OrganizationInvite,
                    OrganizationMembers, OrganizationTeamCreate,
                    OrganizationTeamList, OrganizationTeamMember,
                    OrganizationTeamUpdate, OrganizationUpdate, PluginInfo,
                    SettingsChannelCreateWizard, SettingsChannelDeleteView,
                    SettingsChannelDeprecateView, SettingsChannelListView,
                    SettingsChannelToggleView, SettingsChannelUpdateView,
                    SettingsEmailView, SettingsOAuthView, SettingsView,
                    SetupView, SubscriptionList, UserProfileView, UserRegister,
                    UserWelcomeView, WorkInProgressView, confirm_email,)

urlpatterns = [
    path('setup/', SetupView.as_view(), name='setup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # General
    path('terms/', TemplateView.as_view(template_name='bitcaster/legal/terms.html'), name='legal-terms'),
    path('privacy/', TemplateView.as_view(template_name='bitcaster/legal/privacy.html'), name='legal-privacy'),
    # me
    path('me/', TemplateView.as_view(template_name='bitcaster/me/home.html'), name='me-home'),

    # Settings
    path('settings/', SettingsView.as_view(), name='settings'),
    path('settings/email/', SettingsEmailView.as_view(), name='settings-email'),
    path('settings/oauth/', SettingsOAuthView.as_view(), name='settings-oauth'),
    path('settings/channel/', SettingsChannelListView.as_view(), name='settings-channels'),
    path('settings/channel/add/', SettingsChannelCreateWizard.as_view(), name='system-channel-create'),
    path('settings/channel/<int:pk>/edit/', SettingsChannelUpdateView.as_view(), name='system-channel-update'),
    path('settings/channel/<int:pk>/delete/', SettingsChannelDeleteView.as_view(), name='system-channel-delete'),
    path('settings/channel/<int:pk>/toggle/', SettingsChannelToggleView.as_view(), name='system-channel-toggle'),
    path('settings/channel/<int:pk>/deprecate/', SettingsChannelDeprecateView.as_view(), name='system-channel-deprecate'),
    path('plugins/info/<str:fqn>/', PluginInfo.as_view(), name='plugin-info'),

    # Social
    path('', include('social_django.urls', namespace='social')),
    path('user/register/', UserRegister.as_view(), name='user-register'),
    path('user/register/register-wait-email/<int:pk>/', TemplateView.as_view(template_name='bitcaster/registration/register_wait_email.html'), name='register-wait-email'),
    path('user/register/confirm-email/<int:pk>/<str:check>/', confirm_email, name='confirm-email'),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('new-user/', TemplateView.as_view(template_name='bitcaster/new-user.html')),
    path('new-association/', TemplateView.as_view(template_name='bitcaster/new-association.html')),
    path('login-error/', TemplateView.as_view(template_name='bitcaster/wip.html')),

    # Organization
    path('org/add/', OrganizationCreate.as_view(), name='org-add'),
    path('<slug:org>/details/', OrganizationDetail.as_view(), name='org-index'),
    path('<slug:org>/update/', OrganizationUpdate.as_view(), name='org-config'),

    path('<slug:org>/members/', OrganizationMembers.as_view(), name='org-members'),
    path('<slug:org>/user/<int:pk>/welcome/', UserWelcomeView.as_view(), name='user-welcome'),
    path('<slug:org>/invite/accept/<int:pk>/<str:check>/', InviteAccept.as_view(), name='invitation-accept'),
    path('<slug:org>/invite/delete/<int:pk>/', InviteDelete.as_view(), name='invitation-delete'),
    path('<slug:org>/invite/send/<int:pk>/', InviteSend.as_view(), name='invitation-send'),
    path('<slug:org>/invite/', OrganizationInvite.as_view(), name='org-invite'),

    path('<slug:org>/team/', OrganizationTeamList.as_view(), name='org-team-list'),
    path('<slug:org>/team/add/', OrganizationTeamCreate.as_view(), name='org-team-add'),
    path('<slug:org>/team/<slug:slug>/', OrganizationTeamUpdate.as_view(), name='org-team-update'),
    path('<slug:org>/team/<slug:slug>/members/', OrganizationTeamMember.as_view(), name='org-team-member'),

    path('<slug:org>/channel/', OrganizationChannels.as_view(), name='org-channels'),
    path('<slug:org>/channel/add/', OrganizationChannelCreate.as_view(), name='org-channel-create'),
    path('<slug:org>/channel/<int:pk>/edit/', OrganizationChannelUpdate.as_view(), name='org-channel-update'),
    path('<slug:org>/channel/<int:pk>/delete/', OrganizationChannelRemove.as_view(), name='org-channel-delete'),
    path('<slug:org>/channel/<int:pk>/toggle/', OrganizationChannelToggle.as_view(), name='org-channel-toggle'),
    path('<slug:org>/channel/<int:pk>/deprecate/', OrganizationChannelDeprecate.as_view(), name='org-channel-deprecate'),
    path('<slug:org>/applications/', OrganizationApplications.as_view(), name='org-applications'),
    # Applications
    path('<slug:org>/add/', ApplicationCreate.as_view(), name='application-add'),
    path('<slug:org>/<slug:app>/', ApplicationDetail.as_view(), name='app-index'),
    path('<slug:org>/<slug:app>/subscriptions/', SubscriptionList.as_view(), name='app-subscriptions'),
    path('<slug:org>/<slug:app>/events/', EventList.as_view(), name='app-events'),
    path('<slug:org>/<slug:app>/channel/', ApplicationChannels.as_view(), name='app-channels'),
    path('<slug:org>/<slug:app>/channel/add/', ApplicationChannelCreate.as_view(), name='app-channel-create'),
    path('<slug:org>/<slug:app>/channel/<int:pk>/edit/', ApplicationChannelUpdate.as_view(), name='app-channel-update'),
    path('<slug:org>/<slug:app>/channel/<int:pk>/delete/', ApplicationChannelRemove.as_view(), name='app-channel-delete'),
    path('<slug:org>/<slug:app>/channel/<int:pk>/toggle/', ApplicationChannelToggle.as_view(), name='app-channel-toggle'),
    path('<slug:org>/<slug:app>/channel/<int:pk>/deprecate/', ApplicationChannelDeprecate.as_view(), name='app-channel-deprecate'),
    path('<slug:org>/<slug:app>/messages/', MessageList.as_view(), name='app-messages'),

    path('', IndexView.as_view(), name='index'),
    path('wip/', WorkInProgressView.as_view(), name='wip'),

]
