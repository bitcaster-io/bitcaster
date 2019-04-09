# line too long
# flake8: noqa: E501
from django.conf import settings
from django.urls import include, path, reverse_lazy
from django.views.generic import RedirectView, TemplateView

from bitcaster.web.views import (ApplicationAutocomplete,
                                 ApplicationMembershipDelete,
                                 ApplicationMembershipEdit,
                                 ApplicationMembershipList,
                                 ApplicationTeamMemberRemove,
                                 OrganizationGroupMemberRemove,
                                 OrganizationMembersAutocomplete,
                                 UserAddressesVerifyView,)
from bitcaster.web.views.application.log import ApplicationLog
from bitcaster.web.views.application.members import ApplicationMembershipCreate
from bitcaster.web.views.autocomplete import (ApplicationCandidateAutocomplete,
                                              ApplicationMembersAutocomplete,)
from bitcaster.web.views.settings import (SettingsBackupRestore, SettingsPlugin,
                                          SettingsPluginRefresh,
                                          SettingsPluginToggle,)

from .views import (AddressAutocomplete, ApplicationCheckConfigView,
                    ApplicationCreate, ApplicationDashboard,
                    ApplicationDeleteView, ApplicationInvitationDelete,
                    ApplicationInvitationSend, ApplicationInvite,
                    ApplicationKeyCreate, ApplicationKeyDelete,
                    ApplicationKeyList, ApplicationKeyUpdate,
                    ApplicationMonitorCreate, ApplicationMonitorList,
                    ApplicationMonitorRemove, ApplicationMonitorTest,
                    ApplicationMonitorToggle, ApplicationMonitorUpdate,
                    ApplicationMonitorUsage, ApplicationSubscriptionList,
                    ApplicationTeamCreate, ApplicationTeamDelete,
                    ApplicationTeamList, ApplicationTeamMember,
                    ApplicationTeamUpdate, ApplicationUpdateView,
                    ChannelAutocomplete, EventCreate, EventDelete, EventKeys,
                    EventList, EventMessages, EventSubscriptionCreate,
                    EventSubscriptionDelete, EventSubscriptionInvite,
                    EventSubscriptionList, EventSubscriptionToggle, EventTest,
                    EventToggle, EventUpdate, IndexView, LoginView, LogoutView,
                    MessageCreate, MessageDelete, MessageList, MessageUpdate,
                    OrganizationApplications, OrganizationChannelCreate,
                    OrganizationChannelDeprecate, OrganizationChannelRemove,
                    OrganizationChannels, OrganizationChannelTest,
                    OrganizationChannelToggle, OrganizationChannelUpdate,
                    OrganizationChannelUsage, OrganizationCheckConfigView,
                    OrganizationConfiguration, OrganizationDashboard,
                    OrganizationGroupApplications, OrganizationGroupCreate,
                    OrganizationGroupDelete, OrganizationGroupEdit,
                    OrganizationGroupList, OrganizationGroupMembers,
                    OrganizationMemberInvite, OrganizationMemberInviteAccept,
                    OrganizationMembershipDelete, OrganizationMembershipEdit,
                    OrganizationMembershipList, OrgInviteDelete, OrgInviteSend,
                    PluginInfo, SettingsEmailView, SettingsLdapView,
                    SettingsOAuthView, SettingsSystemInfo, SettingsView,
                    SetupView, UserAddressesAssignmentView,
                    UserAddressesInfoView, UserAddressesView,
                    UserApplicationListView, UserAutocomplete,
                    UserEventListView, UserEventSubcribe, UserHome,
                    UserProfileView, UserSubscriptionEdit,
                    UserSubscriptionListView, UserSubscriptionRemove,
                    UserSubscriptionToggle, WorkInProgressView, channel_icon,
                    confirm_address, confirm_registration, plugin_icon,)

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path(settings.SETUP_URL[1:], SetupView.as_view(), name='setup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('plugins/icons/channel/<int:pk>/', channel_icon, name='channel-icon'),
    path('plugins/icons/<str:fqn>/', plugin_icon, name='plugin-icon'),
    path('plugins/info/<str:fqn>/', PluginInfo.as_view(), name='plugin-info'),

    # General
    path('terms/', TemplateView.as_view(template_name='bitcaster/legal/terms.html'), name='legal-terms'),
    path('privacy/', TemplateView.as_view(template_name='bitcaster/legal/privacy.html'), name='legal-privacy'),

    # Settings
    path('settings/', SettingsView.as_view(), name='settings'),
    path('settings/email/', SettingsEmailView.as_view(), name='settings-email'),
    path('settings/oauth/', SettingsOAuthView.as_view(), name='settings-oauth'),
    path('settings/sysinfo/', SettingsSystemInfo.as_view(), name='settings-sysinfo'),
    path('settings/ldap/', SettingsLdapView.as_view(), name='settings-ldap'),
    path('settings/backup/', SettingsBackupRestore.as_view(), name='settings-backup'),
    path('settings/plugins/<str:type>/', SettingsPlugin.as_view(), name='settings-plugin'),
    path('settings/plugins/<str:type>/<int:pk>/toggle/', SettingsPluginToggle.as_view(), name='settings-plugin-toggle'),
    path('settings/plugins/refresh', SettingsPluginRefresh.as_view(), name='settings-plugin-refresh'),

    # Social
    path('', include('social_django.urls', namespace='social')),
    path('user/register/register-wait-email/<int:pk>/',
         TemplateView.as_view(template_name='bitcaster/registration/register_wait_email.html'),
         name='register-wait-email'),
    path('user/register/confirm-registratiom/<int:pk>/<str:check>/', confirm_registration, name='confirm-registratiom'),
    path('user/register/confirm-address/<int:pk>/<str:address>/<str:check>/', confirm_address, name='confirm-address'),

    # path('me/', UserHome.as_view(), name='me'),
    path('<slug:org>/me/', UserHome.as_view(), name='me'),
    path('<slug:org>/me/events/', UserEventListView.as_view(), name='user-events'),
    path('<slug:org>/me/event/<int:pk>/subscribe/', UserEventSubcribe.as_view(), name='user-event-subscribe'),
    path('<slug:org>/me/subscriptions/', UserSubscriptionListView.as_view(), name='user-subscriptions'),
    path('<slug:org>/me/subscriptions/<int:pk>/toggle/', UserSubscriptionToggle.as_view(),
         name='user-subscription-toggle'),
    path('<slug:org>/me/subscriptions/<int:pk>/delete/', UserSubscriptionRemove.as_view(),
         name='user-subscription-delete'),
    path('<slug:org>/me/subscriptions/<int:pk>/edit/', UserSubscriptionEdit.as_view(), name='user-subscription-edit'),

    path('<slug:org>/me/profile/', UserProfileView.as_view(), name='user-profile'),
    path('<slug:org>/me/addresses/', UserAddressesView.as_view(), name='user-address'),
    path('<slug:org>/me/addresses/<int:pk>/info/', UserAddressesInfoView.as_view(), name='user-address-info'),
    path('<slug:org>/me/assignment/<int:pk>/resend/', UserAddressesVerifyView.as_view(mode='resend'), name='user-address-resend'),
    path('<slug:org>/me/assignment/<int:pk>/verify/', UserAddressesVerifyView.as_view(mode='form'), name='user-address-verify'),
    path('<slug:org>/me/assignment/', UserAddressesAssignmentView.as_view(), name='user-address-assignment'),
    path('<slug:org>/me/applications/', UserApplicationListView.as_view(), name='user-applications'),

    # path('new-user/', TemplateView.as_view(template_name='bitcaster/oauth/user_new.html')),
    # path('new-association/', TemplateView.as_view(template_name='bitcaster/oauth/user_associated.html')),

    path('new-user/', RedirectView.as_view(url=reverse_lazy('me'))),
    path('new-association/', RedirectView.as_view(url=reverse_lazy('me'))),

    path('login-error/',
         TemplateView.as_view(template_name='bitcaster/oauth/login_error.html')),

    # path('user/<slug:org>/', UserHomeView.as_view(), name='user-org'),
    # path('user/<slug:org>/<slug:app>/', UserHomeView.as_view(), name='user-app'),

    # Applications
    path('<slug:org>/a/add/', ApplicationCreate.as_view(), name='application-create'),

    path('<slug:org>/a/<slug:app>/', ApplicationDashboard.as_view(), name='app-dashboard'),
    path('<slug:org>/a/<slug:app>/check/', ApplicationCheckConfigView.as_view(), name='app-check'),
    path('<slug:org>/a/<slug:app>/edit/', ApplicationUpdateView.as_view(), name='app-edit'),
    path('<slug:org>/a/<slug:app>/delete/', ApplicationDeleteView.as_view(), name='app-delete'),

    # Applications / Subscriptions
    path('<slug:org>/a/<slug:app>/subscriptions/', ApplicationSubscriptionList.as_view(), name='app-subscriptions'),

    # Applications / Invitations
    path('<slug:org>/a/<slug:app>/invite/', ApplicationInvite.as_view(), name='app-invite'),
    path('<slug:org>/a/<slug:app>/i/<int:pk>/delete/', ApplicationInvitationDelete.as_view(),
         name='app-invitation-delete'),
    # path('<slug:org>/a/<slug:app>/i/<int:pk>/accept/', ApplicationInvitationAccept.as_view(), name='invitation-accept'),
    path('<slug:org>/a/<slug:app>/i/<int:pk>/send/', ApplicationInvitationSend.as_view(), name='app-invitation-send'),

    # Applications / Member
    path('<slug:org>/a/<slug:app>/member/', ApplicationMembershipList.as_view(), name='app-members'),
    path('<slug:org>/a/<slug:app>/member/<int:pk>/edit/', ApplicationMembershipEdit.as_view(), name='app-member-edit'),
    path('<slug:org>/a/<slug:app>/member/<int:pk>/delete/', ApplicationMembershipDelete.as_view(), name='app-member-delete'),
    path('<slug:org>/a/<slug:app>/member/add/', ApplicationMembershipCreate.as_view(), name='app-member-add'),

    # Applications / Teams
    path('<slug:org>/a/<slug:app>/team/', ApplicationTeamList.as_view(), name='app-teams'),
    path('<slug:org>/a/<slug:app>/team/add/', ApplicationTeamCreate.as_view(), name='app-team-create'),
    path('<slug:org>/a/<slug:app>/team/<int:team>/edit/', ApplicationTeamUpdate.as_view(), name='app-team-edit'),
    path('<slug:org>/a/<slug:app>/team/<int:team>/delete/', ApplicationTeamDelete.as_view(), name='app-team-delete'),
    path('<slug:org>/a/<slug:app>/team/<int:team>/members/', ApplicationTeamMember.as_view(), name='app-team-members'),
    path('<slug:org>/a/<slug:app>/team/<int:team>/members/<int:member>/remove/', ApplicationTeamMemberRemove.as_view(),
         name='app-team-member-remove'),

    # Applications / Keys
    path('<slug:org>/a/<slug:app>/key/', ApplicationKeyList.as_view(), name='app-keys'),
    path('<slug:org>/a/<slug:app>/key/add/', ApplicationKeyCreate.as_view(), name='app-key-create'),
    path('<slug:org>/a/<slug:app>/key/<int:pk>/edit/', ApplicationKeyUpdate.as_view(), name='app-key-edit'),
    path('<slug:org>/a/<slug:app>/key/<int:pk>/delete/', ApplicationKeyDelete.as_view(), name='app-key-delete'),

    # Applications / Events
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
    path('<slug:org>/a/<slug:app>/event/<int:event>/subscriptions/<int:subscription>/delete/',
         EventSubscriptionDelete.as_view(),
         name='app-event-subscription-delete'),
    path('<slug:org>/a/<slug:app>/event/<int:event>/subscriptions/<int:subscription>/toggle/',
         EventSubscriptionToggle.as_view(),
         name='app-event-subscription-toggle'),
    path('<slug:org>/a/<slug:app>/event/<int:event>/subscriptions/invite/', EventSubscriptionInvite.as_view(),
         name='app-event-subscriptions-invite'),

    path('<slug:org>/a/<slug:app>/event/<int:event>/subscriptions/subscribe/', EventSubscriptionCreate.as_view(),
         name='app-event-subscriptions-subscribe'),

    # Applications / Messages
    path('o/<slug:org>/a/<slug:app>/message/', MessageList.as_view(), name='app-messages'),
    path('o/<slug:org>/a/<slug:app>/message/add/', MessageCreate.as_view(), name='app-message-create'),
    path('o/<slug:org>/a/<slug:app>/message/<int:pk>/edit/', MessageUpdate.as_view(), name='app-message-edit'),
    path('o/<slug:org>/a/<slug:app>/message/<int:pk>/delete/', MessageDelete.as_view(), name='app-message-delete'),
    # Log
    path('o/<slug:org>/a/<slug:app>/log/', ApplicationLog.as_view(), name='app-log'),

    # Applications / Monitors
    path('<slug:org>/a/<slug:app>/monitors/', ApplicationMonitorList.as_view(), name='app-monitors'),
    path('<slug:org>/a/<slug:app>/monitor/add/', ApplicationMonitorCreate.as_view(), name='app-monitor-create'),
    path('<slug:org>/a/<slug:app>/monitor/<int:pk>/usage/', ApplicationMonitorUsage.as_view(),
         name='app-monitor-usage'),
    path('<slug:org>/a/<slug:app>/monitor/<int:pk>/edit/', ApplicationMonitorUpdate.as_view(), name='app-monitor-edit'),
    path('<slug:org>/a/<slug:app>/monitor/<int:pk>/delete/', ApplicationMonitorRemove.as_view(),
         name='app-monitor-delete'),
    path('<slug:org>/a/<slug:app>/monitor/<int:pk>/toggle/', ApplicationMonitorToggle.as_view(),
         name='app-monitor-toggle'),
    path('<slug:org>/a/<slug:app>/monitor/<int:pk>/test/', ApplicationMonitorTest.as_view(), name='app-monitor-test'),

    ############
    ## Organization
    # path('org/add/', OrganizationCreate.as_view(), name='org-create'),

    path('<slug:org>/', OrganizationDashboard.as_view(), name='org-home'),

    path('<slug:org>/check/', OrganizationCheckConfigView.as_view(), name='org-check'),
    path('<slug:org>/dashboard', OrganizationDashboard.as_view(), name='org-dashboard'),
    path('<slug:org>/config/', OrganizationConfiguration.as_view(), name='org-config'),

    path('<slug:org>/member/', OrganizationMembershipList.as_view(), name='org-members'),
    path('<slug:org>/member/<int:pk>/edit/', OrganizationMembershipEdit.as_view(), name='org-member-edit'),
    path('<slug:org>/member/<int:pk>/delete/', OrganizationMembershipDelete.as_view(), name='org-member-delete'),

    path('<slug:org>/invite/accept/<int:pk>/<str:check>/', OrganizationMemberInviteAccept.as_view(),
         name='org-member-accept'),
    path('<slug:org>/invite/delete/<int:pk>/', OrgInviteDelete.as_view(), name='org-invitation-delete'),
    path('<slug:org>/invite/send/<int:pk>/', OrgInviteSend.as_view(), name='org-invitation-send'),
    path('<slug:org>/invite/', OrganizationMemberInvite.as_view(), name='org-invite'),

    path('<slug:org>/group/', OrganizationGroupList.as_view(), name='org-groups'),
    path('<slug:org>/group/add/', OrganizationGroupCreate.as_view(), name='org-group-add'),
    path('<slug:org>/group/<int:group>/settings/', OrganizationGroupEdit.as_view(), name='org-group-settings'),
    path('<slug:org>/group/<int:group>/members/', OrganizationGroupMembers.as_view(), name='org-group-members'),
    path('<slug:org>/group/<int:group>/members/<int:member>/remove/', OrganizationGroupMemberRemove.as_view(), name='org-group-member-remove'),
    path('<slug:org>/group/<int:group>/applications/', OrganizationGroupApplications.as_view(),
         name='org-group-applications'),
    path('<slug:org>/group/<int:group>/delete/', OrganizationGroupDelete.as_view(), name='org-group-delete'),

    # path('<slug:org>/team/', OrganizationTeamList.as_view(), name='org-teams'),
    # path('<slug:org>/team/add/', OrganizationTeamCreate.as_view(), name='org-team-create'),
    # path('<slug:org>/team/<slug:slug>/edit/', OrganizationTeamUpdate.as_view(), name='org-team-edit'),
    # path('<slug:org>/team/<slug:slug>/delete/', OrganizationTeamDelete.as_view(), name='org-team-delete'),
    # path('<slug:org>/team/<slug:slug>/members/', OrganizationTeamMember.as_view(), name='org-team-member'),

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

    # path('tpl/<str:path>', PreviewView.as_view(), name='wip'),

]

urlpatterns += [
    path('dal/user-autocomplete/', UserAutocomplete.as_view(), name='user-autocomplete'),
    path('dal/address-autocomplete/', AddressAutocomplete.as_view(), name='address-autocomplete'),
    path('dal/channel-autocomplete/', ChannelAutocomplete.as_view(), name='channel-autocomplete'),

    path('dal/<slug:org>/application-autocomplete/', ApplicationAutocomplete.as_view(), name='application-autocomplete'),
    path('dal/<slug:org>/members-autocomplete/', OrganizationMembersAutocomplete.as_view(), name='org-member-autocomplete'),

    path('dal/<slug:org>/a/<slug:app>/members-autocomplete/', ApplicationMembersAutocomplete.as_view(), name='app-member-autocomplete'),
    path('dal/<slug:org>/a/<slug:app>/candidate-autocomplete/', ApplicationCandidateAutocomplete.as_view(), name='app-candidate-autocomplete'),
]
