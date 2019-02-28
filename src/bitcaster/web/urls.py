# line too long
# flake8: noqa: E501
from django.conf import settings
from django.urls import include, path
from django.views.generic import TemplateView

from bitcaster.web.views.callbacks import confirm_address
from bitcaster.web.views.user import UserIndexView
from bitcaster.web.views.views import PreviewView

from .views import (ApplicationCheckConfigView, ApplicationCreate,  # 
                    ApplicationDashboard, ApplicationDeleteView,
                    ApplicationKeyCreate, ApplicationKeyDelete,
                    ApplicationKeyList, ApplicationKeyUpdate,
                    ApplicationMonitorCreate, ApplicationMonitorList,
                    ApplicationMonitorRemove, ApplicationMonitorTest,
                    ApplicationMonitorToggle, ApplicationMonitorUpdate,
                    ApplicationMonitorUsage, ApplicationSubscriptionList,
                    ApplicationTeamList, ApplicationUpdateView, EventCreate,
                    EventDelete, EventKeys, EventList, EventMessages,
                    EventSubscriptionCreate, EventSubscriptionDelete,
                    EventSubscriptionInvite, EventSubscriptionList,
                    EventSubscriptionToggle, EventTest, EventToggle,
                    EventUpdate, IndexView, InviteAccept, InviteDelete,
                    InviteSend, LoginView, LogoutView, MessageCreate,
                    MessageDelete, MessageList, MessageUpdate,
                    OrganizationApplications, OrganizationChannelCreate,
                    OrganizationChannelDeprecate, OrganizationChannelRemove,
                    OrganizationChannels, OrganizationChannelTest,
                    OrganizationChannelToggle, OrganizationChannelUpdate,
                    OrganizationChannelUsage, OrganizationCheckConfigView,
                    OrganizationConfiguration, OrganizationDashboard,
                    OrganizationInvite, OrganizationMembershipDelete,
                    OrganizationMembershipEdit, OrganizationMembershipList,
                    OrganizationTeamCreate, OrganizationTeamDelete,
                    OrganizationTeamList, OrganizationTeamMember,
                    OrganizationTeamUpdate, PluginInfo, SettingsEmailView,
                    SettingsOAuthView, SettingsSystemInfo, SettingsView,
                    SetupView, UserAddressesAssignmentView,
                    UserAddressesInfoView, UserAddressesView, UserProfileView,
                    UserRegister, WorkInProgressView, confirm_registration,)

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path(settings.SETUP_URL[1:], SetupView.as_view(), name='setup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # General
    path('terms/', TemplateView.as_view(template_name='bitcaster/legal/terms.html'), name='legal-terms'),
    path('privacy/', TemplateView.as_view(template_name='bitcaster/legal/privacy.html'), name='legal-privacy'),

    # Settings
    path('settings/', SettingsView.as_view(), name='settings'),
    path('settings/email/', SettingsEmailView.as_view(), name='settings-email'),
    path('settings/oauth/', SettingsOAuthView.as_view(), name='settings-oauth'),
    path('settings/sysinfo/', SettingsSystemInfo.as_view(), name='settings-sysinfo'),
    # path('settings/organizations/', SettingsOrgListView.as_view(), name='settings-org-list'),
    # path('settings/organizations/<int:pk>/edit/', SettingsOrgUpdateView.as_view(),
    #      name='settings-org-update'),
    # path('settings/channel/', SettingsChannelListView.as_view(), name='settings-channels'),
    # path('settings/channel/add/', SettingsChannelCreateWizard.as_view(), name='system-channel-create'),
    # path('settings/channel/<int:pk>/edit/', SettingsChannelUpdateView.as_view(), name='system-channel-update'),
    # path('settings/channel/<int:pk>/delete/', SettingsChannelDeleteView.as_view(), name='system-channel-delete'),
    # path('settings/channel/<int:pk>/toggle/', SettingsChannelToggleView.as_view(), name='system-channel-toggle'),
    # path('settings/channel/<int:pk>/deprecate/', SettingsChannelDeprecateView.as_view(),
    #      name='system-channel-deprecate'),

    path('plugins/info/<str:fqn>/', PluginInfo.as_view(), name='plugin-info'),

    # Social
    path('', include('social_django.urls', namespace='social')),
    path('user/register/', UserRegister.as_view(), name='user-register'),
    path('user/register/register-wait-email/<int:pk>/',
         TemplateView.as_view(template_name='bitcaster/registration/register_wait_email.html'),
         name='register-wait-email'),
    path('user/register/confirm-registratiom/<int:pk>/<str:check>/', confirm_registration, name='confirm-registratiom'),
    path('user/register/confirm-address/<int:pk>/<str:address>/<str:check>/', confirm_address, name='confirm-address'),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('user/addresses/', UserAddressesView.as_view(), name='user-addresses'),
    path('user/addresses/<int:pk>/info', UserAddressesInfoView.as_view(), name='user-address-info'),
    path('user/assignment/', UserAddressesAssignmentView.as_view(), name='user-address-assignment'),

    path('new-user/', TemplateView.as_view(template_name='bitcaster/users/user_new.html')),
    path('new-association/', TemplateView.as_view(template_name='bitcaster/users/user_associated.html')),
    path('login-error/', TemplateView.as_view(template_name='bitcaster/users/login_error.html')),

    # path('user/<slug:org>/', UserHomeView.as_view(), name='user-org'),
    # path('user/<slug:org>/<slug:app>/', UserHomeView.as_view(), name='user-app'),

    # Applications
    path('<slug:org>/a/add/', ApplicationCreate.as_view(), name='application-create'),

    path('<slug:org>/a/<slug:app>/', ApplicationDashboard.as_view(), name='app-dashboard'),
    path('<slug:org>/a/<slug:app>/check/', ApplicationCheckConfigView.as_view(), name='app-check'),
    path('<slug:org>/a/<slug:app>/edit/', ApplicationUpdateView.as_view(), name='app-edit'),
    path('<slug:org>/a/<slug:app>/delete/', ApplicationDeleteView.as_view(), name='app-delete'),
    path('<slug:org>/a/<slug:app>/subscriptions/', ApplicationSubscriptionList.as_view(), name='app-subscriptions'),

    path('<slug:org>/a/<slug:app>/key/', ApplicationKeyList.as_view(), name='app-keys'),
    path('<slug:org>/a/<slug:app>/key/add/', ApplicationKeyCreate.as_view(), name='app-key-create'),
    path('<slug:org>/a/<slug:app>/key/<int:pk>/edit/', ApplicationKeyUpdate.as_view(), name='app-key-edit'),
    path('<slug:org>/a/<slug:app>/key/<int:pk>/delete/', ApplicationKeyDelete.as_view(), name='app-key-delete'),

    path('<slug:org>/a/<slug:app>/event/', EventList.as_view(), name='app-events'),
    path('<slug:org>/a/<slug:app>/event/add/', EventCreate.as_view(), name='app-event-create'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/edit/', EventUpdate.as_view(), name='app-event-edit'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/toggle/', EventToggle.as_view(), name='app-event-toggle'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/test/', EventTest.as_view(), name='app-event-test'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/delete/', EventDelete.as_view(), name='app-event-delete'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/messages/', EventMessages.as_view(), name='app-event-messages'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/keys/', EventKeys.as_view(), name='app-event-keys'),

    path('<slug:org>/a/<slug:app>/event/<int:event>/subscriptions/', EventSubscriptionList.as_view(),
         name='app-event-subscriptions'),
    path('<slug:org>/a/<slug:app>/event/<int:event>/subscriptions/<int:subscription>/delete/', EventSubscriptionDelete.as_view(),
         name='app-event-subscription-delete'),
    path('<slug:org>/a/<slug:app>/event/<int:event>/subscriptions/<int:subscription>/toggle/', EventSubscriptionToggle.as_view(),
         name='app-event-subscription-toggle'),
    path('<slug:org>/a/<slug:app>/event/<int:event>/subscriptions/invite/', EventSubscriptionInvite.as_view(),
         name='app-event-subscriptions-invite'),

    path('<slug:org>/a/<slug:app>/event/<int:event>/subscriptions/subscribe/', EventSubscriptionCreate.as_view(),
         name='app-event-subscribe'),

    path('<slug:org>/a/<slug:app>/monitors/', ApplicationMonitorList.as_view(), name='app-monitors'),
    path('<slug:org>/a/<slug:app>/monitor/add/', ApplicationMonitorCreate.as_view(), name='app-monitor_create'),
    path('<slug:org>/a/<slug:app>/monitor/<int:pk>/usage/', ApplicationMonitorUsage.as_view(), name='app-monitor-usage'),
    path('<slug:org>/a/<slug:app>/monitor/<int:pk>/edit/', ApplicationMonitorUpdate.as_view(), name='app-monitor-edit'),
    path('<slug:org>/a/<slug:app>/monitor/<int:pk>/delete/', ApplicationMonitorRemove.as_view(), name='app-monitor-delete'),
    path('<slug:org>/a/<slug:app>/monitor/<int:pk>/toggle/', ApplicationMonitorToggle.as_view(), name='app-monitor-toggle'),
    path('<slug:org>/a/<slug:app>/monitor/<int:pk>/test/', ApplicationMonitorTest.as_view(), name='app-monitor-test'),

    # path('<slug:org>/a/<slug:app>/channel/', ApplicationChannels.as_view(), name='app-channel-list'),
    # path('<slug:org>/a/<slug:app>/channel/add/', ApplicationChannelCreate.as_view(), name='app-channel-create'),
    # path('<slug:org>/a/<slug:app>/channel/<int:pk>/edit/', ApplicationChannelUpdate.as_view(),
    #      name='app-channel-update'),
    # path('<slug:org>/a/<slug:app>/channel/<int:pk>/delete/', ApplicationChannelRemove.as_view(),
    #      name='app-channel-delete'),
    # path('<slug:org>/a/<slug:app>/channel/<int:pk>/toggle/', ApplicationChannelToggle.as_view(),
    #      name='app-channel-toggle'),
    # path('<slug:org>/a/<slug:app>/channel/<int:pk>/deprecate/', ApplicationChannelDeprecate.as_view(),
    #      name='app-channel-deprecate'),

    path('o/<slug:org>/a/<slug:app>/team/', ApplicationTeamList.as_view(), name='app-teams'),

    path('o/<slug:org>/a/<slug:app>/message/', MessageList.as_view(), name='app-messages'),
    path('o/<slug:org>/a/<slug:app>/message/add/', MessageCreate.as_view(), name='app-message-create'),
    path('o/<slug:org>/a/<slug:app>/message/<int:pk>/edit/', MessageUpdate.as_view(), name='app-message-edit'),
    path('o/<slug:org>/a/<slug:app>/message/<int:pk>/delete/', MessageDelete.as_view(), name='app-message-delete'),

    # Organization
    # path('org/add/', OrganizationCreate.as_view(), name='org-create'),

    path('<slug:org>/', UserIndexView.as_view(), name='me'),
    path('<slug:org>/check/', OrganizationCheckConfigView.as_view(), name='org-check'),
    path('<slug:org>/dashboard', OrganizationDashboard.as_view(), name='org-dashboard'),
    path('<slug:org>/config/', OrganizationConfiguration.as_view(), name='org-config'),

    path('<slug:org>/member/', OrganizationMembershipList.as_view(), name='org-members'),
    # path('<slug:org>/member/add/', OrganizationCreateMember.as_view(), name='org-member-register'),
    path('<slug:org>/member/<int:pk>/edit/', OrganizationMembershipEdit.as_view(), name='org-member-edit'),
    path('<slug:org>/member/<int:pk>/delete/', OrganizationMembershipDelete.as_view(), name='org-member-delete'),
    path('<slug:org>/invite/accept/<int:pk>/<str:check>/', InviteAccept.as_view(), name='org-member-accept'),
    path('<slug:org>/invite/delete/<int:pk>/', InviteDelete.as_view(), name='org-invite-delete'),
    path('<slug:org>/invite/send/<int:pk>/', InviteSend.as_view(), name='org-member-send'),
    path('<slug:org>/invite/', OrganizationInvite.as_view(), name='org-invite'),

    path('<slug:org>/team/', OrganizationTeamList.as_view(), name='org-teams'),
    path('<slug:org>/team/add/', OrganizationTeamCreate.as_view(), name='org-team-create'),
    path('<slug:org>/team/<slug:slug>/edit/', OrganizationTeamUpdate.as_view(), name='org-team-edit'),
    path('<slug:org>/team/<slug:slug>/delete/', OrganizationTeamDelete.as_view(), name='org-team-delete'),
    path('<slug:org>/team/<slug:slug>/members/', OrganizationTeamMember.as_view(), name='org-team-member'),

    path('<slug:org>/channel/', OrganizationChannels.as_view(), name='org-channels'),
    path('<slug:org>/channel/add/', OrganizationChannelCreate.as_view(), name='org-channel-create'),
    path('<slug:org>/channel/<int:pk>/usage/', OrganizationChannelUsage.as_view(), name='org-channel-usage'),
    path('<slug:org>/channel/<int:pk>/edit/', OrganizationChannelUpdate.as_view(), name='org-channel-edit'),
    path('<slug:org>/channel/<int:pk>/delete/', OrganizationChannelRemove.as_view(), name='org-channel-delete'),
    path('<slug:org>/channel/<int:pk>/toggle/', OrganizationChannelToggle.as_view(), name='org-channel-toggle'),
    path('<slug:org>/channel/<int:pk>/test/', OrganizationChannelTest.as_view(), name='org-channel-test'),
    path('<slug:org>/channel/<int:pk>/deprecate/', OrganizationChannelDeprecate.as_view(),
         name='org-channel-deprecate'),

    path('<slug:org>/applications/', OrganizationApplications.as_view(), name='org-applications'),

    path('wip/', WorkInProgressView.as_view(), name='wip'),

    path('tpl/<str:path>', PreviewView.as_view(), name='wip'),

]
