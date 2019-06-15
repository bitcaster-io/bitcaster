# line too long
# flake8: noqa: E501
from django.conf import settings
from django.urls import include, path, reverse_lazy
from django.views.generic import RedirectView, TemplateView

from bitcaster.utils.impersonate import impersonate_start, impersonate_stop

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path(settings.SETUP_URL[1:], views.SetupView.as_view(), name='setup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('plugins/icons/channel/<int:pk>/', views.channel_icon, name='channel-icon'),
    path('plugins/icons/<str:fqn>/', views.plugin_icon, name='plugin-icon'),
    path('plugins/info/<str:fqn>/', views.PluginInfo.as_view(), name='plugin-info'),

    # General
    # path('terms/', TemplateView.as_view(template_name='bitcaster/legal/terms.html'), name='legal-terms'),
    # path('privacy/', TemplateView.as_view(template_name='bitcaster/legal/privacy.html'), name='legal-privacy'),

    # Settings
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('settings/services/', views.SettingsServicesView.as_view(), name='settings-services'),
    path('settings/email/', views.SettingsEmailView.as_view(), name='settings-email'),
    path('settings/oauth/', views.SettingsOAuthView.as_view(), name='settings-oauth'),
    path('settings/sysinfo/', views.SettingsSystemInfo.as_view(), name='settings-sysinfo'),
    path('settings/ldap/', views.SettingsLdapView.as_view(), name='settings-ldap'),
    path('settings/backup/', views.SettingsBackupRestore.as_view(), name='settings-backup'),
    path('settings/plugins/<str:type>/', views.SettingsPlugin.as_view(), name='settings-plugin'),
    path('settings/plugins/<str:type>/<int:pk>/toggle/', views.SettingsPluginToggle.as_view(),
         name='settings-plugin-toggle'),
    path('settings/plugins/refresh', views.SettingsPluginRefresh.as_view(), name='settings-plugin-refresh'),

    # Message
    path('confirmation/<int:event>/<int:subscription>/<int:channel>/<int:occurence>/<str:code>/',
         views.confirmation, name='confirmation'),
    path('pixel/<int:event>/<int:subscription>/<int:channel>/<int:code>/',
         views.pixel, name='pixel'),

    # Social
    path('', include('social_django.urls', namespace='social')),
    # path('user/register/register-wait-email/<int:pk>/',
    #      TemplateView.as_view(template_name='bitcaster/registration/register_wait_email.html'),
    #      name='register-wait-email'),
    path('user/register/confirm-registratiom/<int:pk>/<str:check>/', views.confirm_registration,
         name='confirm-registratiom'),
    path('user/register/confirm-address/<int:pk>/<str:address>/<str:check>/', views.confirm_address,
         name='confirm-address'),

    path('me/', views.IndexView.as_view()),
    path('<slug:org>/me/', views.UserHome.as_view(), name='me'),
    path('<slug:org>/me/events/', views.UserEventListView.as_view(), name='user-events'),
    path('<slug:org>/me/social/', views.UserSocialAuthView.as_view(), name='user-socialauth'),
    path('<slug:org>/me/social/<str:provider>/disconnect/', views.UserSocialAuthDisconnectView.as_view(),
         name='user-socialauth-disconnect'),
    path('<slug:org>/me/event/<int:pk>/subscribe/', views.UserEventSubcribe.as_view(), name='user-event-subscribe'),
    path('<slug:org>/me/subscriptions/', views.UserSubscriptionListView.as_view(), name='user-subscriptions'),
    path('<slug:org>/me/subscriptions/<int:pk>/toggle/', views.UserSubscriptionToggle.as_view(),
         name='user-subscription-toggle'),
    path('<slug:org>/me/subscriptions/<int:pk>/delete/', views.UserSubscriptionRemove.as_view(),
         name='user-subscription-delete'),
    path('<slug:org>/me/subscriptions/<int:pk>/edit/', views.UserSubscriptionEdit.as_view(),
         name='user-subscription-edit'),

    path('<slug:org>/me/profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('<slug:org>/me/addresses/', views.UserAddressesView.as_view(), name='user-address'),
    path('<slug:org>/me/addresses/<int:pk>/info/', views.UserAddressesInfoView.as_view(), name='user-address-info'),
    path('<slug:org>/me/assignment/<int:pk>/resend/', views.UserAddressesVerifyView.as_view(mode='resend'),
         name='user-address-resend'),
    path('<slug:org>/me/assignment/<int:pk>/verify/', views.UserAddressesVerifyView.as_view(mode='form'),
         name='user-address-verify'),
    path('<slug:org>/me/assignment/', views.UserAddressesAssignmentView.as_view(), name='user-address-assignment'),
    path('<slug:org>/me/applications/', views.UserApplicationListView.as_view(), name='user-applications'),
    path('<slug:org>/me/logs/', views.UserNotificationLogView.as_view(), name='user-logs'),

    # path('new-user/', TemplateView.as_view(template_name='bitcaster/oauth/user_new.html')),
    # path('new-association/', TemplateView.as_view(template_name='bitcaster/oauth/user_associated.html')),

    path('new-user/', RedirectView.as_view(url=reverse_lazy('me'))),
    path('new-association/', RedirectView.as_view(url=reverse_lazy('me'))),

    path('login-error/',
         TemplateView.as_view(template_name='bitcaster/oauth/login_error.html')),

    # path('user/<slug:org>/', UserHomeView.as_view(), name='user-org'),
    # path('user/<slug:org>/<slug:app>/', UserHomeView.as_view(), name='user-app'),

    # Applications
    path('<slug:org>/a/add/', views.ApplicationCreate.as_view(), name='application-create'),

    path('<slug:org>/a/<slug:app>/', views.ApplicationDashboard.as_view(), name='app-dashboard'),
    path('<slug:org>/a/<slug:app>/check/', views.ApplicationCheckConfigView.as_view(), name='app-check'),
    path('<slug:org>/a/<slug:app>/edit/', views.ApplicationUpdateView.as_view(), name='app-edit'),
    path('<slug:org>/a/<slug:app>/delete/', views.ApplicationDeleteView.as_view(), name='app-delete'),

    # Applications / Subscriptions
    path('<slug:org>/a/<slug:app>/subscriptions/', views.ApplicationSubscriptionList.as_view(),
         name='app-subscriptions'),

    # Applications / Invitations
    path('<slug:org>/a/<slug:app>/invite/', views.ApplicationInvite.as_view(), name='app-invite'),
    path('<slug:org>/a/<slug:app>/i/<int:pk>/delete/', views.ApplicationInvitationDelete.as_view(),
         name='app-invitation-delete'),
    # path('<slug:org>/a/<slug:app>/i/<int:pk>/accept/', ApplicationInvitationAccept.as_view(), name='invitation-accept'),
    path('<slug:org>/a/<slug:app>/i/<int:pk>/send/', views.ApplicationInvitationSend.as_view(),
         name='app-invitation-send'),

    # Applications / Member
    path('<slug:org>/a/<slug:app>/member/', views.ApplicationMembershipList.as_view(), name='app-members'),
    path('<slug:org>/a/<slug:app>/member/<int:pk>/edit/', views.ApplicationMembershipEdit.as_view(),
         name='app-member-edit'),
    path('<slug:org>/a/<slug:app>/member/<int:pk>/delete/', views.ApplicationMembershipDelete.as_view(),
         name='app-member-delete'),
    path('<slug:org>/a/<slug:app>/member/add/', views.ApplicationMembershipCreate.as_view(), name='app-member-add'),

    # Applications / Teams
    path('<slug:org>/a/<slug:app>/team/', views.ApplicationTeamList.as_view(), name='app-teams'),
    path('<slug:org>/a/<slug:app>/team/add/', views.ApplicationTeamCreate.as_view(), name='app-team-create'),
    path('<slug:org>/a/<slug:app>/team/<int:team>/edit/', views.ApplicationTeamUpdate.as_view(), name='app-team-edit'),
    path('<slug:org>/a/<slug:app>/team/<int:team>/delete/', views.ApplicationTeamDelete.as_view(),
         name='app-team-delete'),
    path('<slug:org>/a/<slug:app>/team/<int:team>/members/', views.ApplicationTeamMember.as_view(),
         name='app-team-members'),
    path('<slug:org>/a/<slug:app>/team/<int:team>/members/<int:member>/remove/',
         views.ApplicationTeamMemberRemove.as_view(),
         name='app-team-member-remove'),

    # Applications / Keys
    path('<slug:org>/a/<slug:app>/key/', views.ApplicationKeyList.as_view(), name='app-keys'),
    path('<slug:org>/a/<slug:app>/key/add/', views.ApplicationKeyCreate.as_view(), name='app-key-create'),
    path('<slug:org>/a/<slug:app>/key/<int:pk>/edit/', views.ApplicationKeyUpdate.as_view(), name='app-key-edit'),
    path('<slug:org>/a/<slug:app>/key/<int:pk>/delete/', views.ApplicationKeyDelete.as_view(), name='app-key-delete'),

    # Applications / Events
    path('<slug:org>/a/<slug:app>/event/', views.EventList.as_view(), name='app-events'),
    path('<slug:org>/a/<slug:app>/event/add/', views.EventCreate.as_view(), name='app-event-create'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/edit/', views.EventUpdate.as_view(), name='app-event-edit'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/dev-mode/', views.EventDeveloperModeToggle.as_view(), name='app-event-develop'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/toggle/', views.EventToggle.as_view(), name='app-event-toggle'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/test/', views.EventTest.as_view(), name='app-event-test'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/batch/', views.EventBatch.as_view(), name='app-event-batch'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/bee/', views.EventBee.as_view(), name='app-event-bee'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/delete/', views.EventDelete.as_view(), name='app-event-delete'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/messages/', views.EventMessages.as_view(), name='app-event-messages'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/keys/', views.EventKeys.as_view(), name='app-event-keys'),

    path('<slug:org>/a/<slug:app>/event/<int:event>/subscriptions/', views.EventSubscriptionList.as_view(),
         name='app-event-subscriptions'),
    path('<slug:org>/a/<slug:app>/event/<int:event>/subscriptions/<int:subscription>/delete/',
         views.EventSubscriptionDelete.as_view(),
         name='app-event-subscription-delete'),
    path('<slug:org>/a/<slug:app>/event/<int:event>/subscriptions/<int:subscription>/toggle/',
         views.EventSubscriptionToggle.as_view(),
         name='app-event-subscription-toggle'),
    path('<slug:org>/a/<slug:app>/event/<int:event>/subscriptions/invite/', views.EventSubscriptionInvite.as_view(),
         name='app-event-subscriptions-invite'),

    path('<slug:org>/a/<slug:app>/event/<int:event>/subscriptions/subscribe/', views.EventSubscriptionCreate.as_view(),
         name='app-event-subscriptions-subscribe'),

    # Applications / Messages
    path('o/<slug:org>/a/<slug:app>/message/', views.MessageList.as_view(), name='app-messages'),
    path('o/<slug:org>/a/<slug:app>/message/add/', views.MessageCreate.as_view(), name='app-message-create'),
    path('o/<slug:org>/a/<slug:app>/message/<int:pk>/edit/', views.MessageUpdate.as_view(), name='app-message-edit'),
    path('o/<slug:org>/a/<slug:app>/message/<int:pk>/delete/', views.MessageDelete.as_view(),
         name='app-message-delete'),
    # Log
    path('o/<slug:org>/a/<slug:app>/log/', views.ApplicationNotificationLog.as_view(), name='app-log'),

    # views.Applications / FileGetter
    path('<slug:org>/a/<slug:app>/files/', views.ApplicationFileGetterList.as_view(), name='app-filegetters'),
    path('<slug:org>/a/<slug:app>/files/add/', views.ApplicationFileGetterCreate.as_view(), name='app-filegetter-create'),
    path('<slug:org>/a/<slug:app>/files/<int:pk>/usage/', views.ApplicationFileGetterUsage.as_view(),
         name='app-filegetter-usage'),
    path('<slug:org>/a/<slug:app>/files/<int:pk>/edit/', views.ApplicationFileGetterUpdate.as_view(),
         name='app-filegetter-edit'),
    path('<slug:org>/a/<slug:app>/files/<int:pk>/delete/', views.ApplicationFileGetterRemove.as_view(),
         name='app-filegetter-delete'),
    path('<slug:org>/a/<slug:app>/files/<int:pk>/toggle/', views.ApplicationFileGetterToggle.as_view(),
         name='app-filegetter-toggle'),
    path('<slug:org>/a/<slug:app>/files/<int:pk>/poll/', views.ApplicationFileGetterPoll.as_view(),
         name='app-filegetter-poll'),

    path('<slug:org>/a/<slug:app>/files/<int:pk>/test/', views.ApplicationFileGetterTest.as_view(),
         name='app-filegetter-test'),

    # views.Applications / Monitors
    path('<slug:org>/a/<slug:app>/monitors/', views.ApplicationMonitorList.as_view(), name='app-monitors'),
    path('<slug:org>/a/<slug:app>/monitor/add/', views.ApplicationMonitorCreate.as_view(), name='app-monitor-create'),
    path('<slug:org>/a/<slug:app>/monitor/<int:pk>/usage/', views.ApplicationMonitorUsage.as_view(),
         name='app-monitor-usage'),
    path('<slug:org>/a/<slug:app>/monitor/<int:pk>/edit/', views.ApplicationMonitorUpdate.as_view(),
         name='app-monitor-edit'),
    path('<slug:org>/a/<slug:app>/monitor/<int:pk>/delete/', views.ApplicationMonitorRemove.as_view(),
         name='app-monitor-delete'),
    path('<slug:org>/a/<slug:app>/monitor/<int:pk>/toggle/', views.ApplicationMonitorToggle.as_view(),
         name='app-monitor-toggle'),
    path('<slug:org>/a/<slug:app>/monitor/<int:pk>/poll/', views.ApplicationMonitorPoll.as_view(),
         name='app-monitor-poll'),

    path('<slug:org>/a/<slug:app>/monitor/<int:pk>/test/', views.ApplicationMonitorTest.as_view(),
         name='app-monitor-test'),

    ############
    ## Organization
    # path('org/add/', views.OrganizationCreate.as_view(), name='org-create'),

    path('<slug:org>/', views.OrganizationDashboard.as_view(), name='org-home'),

    path('<slug:org>/check/', views.OrganizationCheckConfigView.as_view(), name='org-check'),
    path('<slug:org>/dashboard', views.OrganizationDashboard.as_view(), name='org-dashboard'),
    path('<slug:org>/config/', views.OrganizationConfiguration.as_view(), name='org-config'),
    path('<slug:org>/log/', views.OrganizationNotificationLogView.as_view(), name='org-log'),
    path('<slug:org>/audit/', views.OrganizationAuditLogView.as_view(), name='org-auditlog'),
    path('<slug:org>/errors/', views.OrganizationErrorLogView.as_view(), name='org-errorlog'),

    path('<slug:org>/member/', views.OrganizationMembershipList.as_view(), name='org-members'),
    path('<slug:org>/member/<int:pk>/edit/', views.OrganizationMembershipEdit.as_view(), name='org-member-edit'),
    path('<slug:org>/member/<int:pk>/delete/', views.OrganizationMembershipDelete.as_view(), name='org-member-delete'),

    path('<slug:org>/invite/accept/<int:pk>/<str:check>/', views.OrganizationMemberInviteAccept.as_view(),
         name='org-member-accept'),
    path('<slug:org>/invite/delete/<int:pk>/', views.OrgInviteDelete.as_view(), name='org-invitation-delete'),
    path('<slug:org>/invite/send/<int:pk>/', views.OrgInviteSend.as_view(), name='org-invitation-send'),
    path('<slug:org>/invite/', views.OrganizationMemberInvite.as_view(), name='org-invite'),

    path('<slug:org>/group/', views.OrganizationGroupList.as_view(), name='org-groups'),
    path('<slug:org>/group/add/', views.OrganizationGroupCreate.as_view(), name='org-group-add'),
    path('<slug:org>/group/<int:group>/settings/', views.OrganizationGroupEdit.as_view(), name='org-group-settings'),
    path('<slug:org>/group/<int:group>/members/', views.OrganizationGroupMembers.as_view(), name='org-group-members'),
    path('<slug:org>/group/<int:group>/members/<int:member>/remove/', views.OrganizationGroupMemberRemove.as_view(),
         name='org-group-member-remove'),
    path('<slug:org>/group/<int:group>/applications/', views.OrganizationGroupApplications.as_view(),
         name='org-group-applications'),
    path('<slug:org>/group/<int:group>/delete/', views.OrganizationGroupDelete.as_view(), name='org-group-delete'),

    # path('<slug:org>/team/', views.OrganizationTeamList.as_view(), name='org-teams'),
    # path('<slug:org>/team/add/', views.OrganizationTeamCreate.as_view(), name='org-team-create'),
    # path('<slug:org>/team/<slug:slug>/edit/', views.OrganizationTeamUpdate.as_view(), name='org-team-edit'),
    # path('<slug:org>/team/<slug:slug>/delete/', views.OrganizationTeamDelete.as_view(), name='org-team-delete'),
    # path('<slug:org>/team/<slug:slug>/members/', views.OrganizationTeamMember.as_view(), name='org-team-member'),

    path('<slug:org>/channel/', views.OrganizationChannels.as_view(), name='org-channels'),
    path('<slug:org>/channel/add/', views.OrganizationChannelCreate.as_view(), name='org-channel-create'),
    path('<slug:org>/channel/<int:pk>/usage/', views.OrganizationChannelUsage.as_view(), name='org-channel-usage'),
    path('<slug:org>/channel/<int:pk>/edit/', views.OrganizationChannelUpdate.as_view(), name='org-channel-edit'),
    path('<slug:org>/channel/<int:pk>/delete/', views.OrganizationChannelRemove.as_view(), name='org-channel-delete'),
    path('<slug:org>/channel/<int:pk>/toggle/', views.OrganizationChannelToggle.as_view(), name='org-channel-toggle'),
    path('<slug:org>/channel/<int:pk>/test/', views.OrganizationChannelTest.as_view(), name='org-channel-test'),
    path('<slug:org>/channel/<int:pk>/deprecate/', views.OrganizationChannelDeprecate.as_view(),
         name='org-channel-deprecate'),

    path('<slug:org>/charts/audit/', views.audit_log, name='org-charts-audit'),
    path('<slug:org>/charts/notification/', views.notification_log, name='org-charts-notification'),
    path('<slug:org>/charts/occurence/', views.occurence_log, name='org-charts-occurence'),
    path('<slug:org>/charts/error/', views.error_log, name='org-charts-errors'),
    path('<slug:org>/charts/buffers/<str:name>/', views.get_buffers, name='org-charts-buffers'),

    path('<slug:org>/<slug:app>/charts/audit/', views.audit_log, name='app-charts-audit'),
    path('<slug:org>/<slug:app>/charts/notification/', views.notification_log, name='app-charts-notification'),
    path('<slug:org>/<slug:app>/charts/occurence/', views.occurence_log, name='app-charts-occurence'),
    path('<slug:org>/<slug:app>/charts/error/', views.error_log, name='app-charts-errors'),
    path('<slug:org>/<slug:app>/charts/buffers/<str:name>/', views.get_buffers, name='app-charts-buffers'),

    # path('trigger/<str:task_fqn>/', views.trigger_task, name='org-charts-buffers'),

    path('<slug:org>/applications/', views.OrganizationApplications.as_view(), name='org-applications'),

    # path('wip/', views.WorkInProgressView.as_view(), name='wip'),
    #
    # path('tpl/<str:path>', PreviewView.as_view(), name='wip'),

]

# locks
urlpatterns += [
    path('locks/<slug:org>/<str:lock_name>/unlock/', views.unlock, name='locks-unlock'),
    path('locks/<slug:org>/', views.lock_list, name='locks-list'),
]

urlpatterns += [
    path('dal/user-autocomplete/', views.UserAutocomplete.as_view(), name='user-autocomplete'),
    path('dal/address-autocomplete/', views.AddressAutocomplete.as_view(), name='address-autocomplete'),
    path('dal/<slug:org>/channel-autocomplete/', views.ChannelAutocomplete.as_view(), name='channel-autocomplete'),

    path('dal/<slug:org>/application-autocomplete/', views.ApplicationAutocomplete.as_view(),
         name='application-autocomplete'),
    path('dal/<slug:org>/members-autocomplete/', views.OrganizationMembersAutocomplete.as_view(),
         name='org-member-autocomplete'),

    path('dal/<slug:org>/a/<slug:app>/members-autocomplete/', views.ApplicationMembersAutocomplete.as_view(),
         name='app-member-autocomplete'),
    path('dal/<slug:org>/a/<slug:app>/candidate-autocomplete/', views.ApplicationCandidateAutocomplete.as_view(),
         name='app-candidate-autocomplete'),
]

urlpatterns += (
    path('impersonate/stop/', impersonate_stop, name='impersonate-stop'),
    path('impersonate/<int:uid>/', impersonate_start, name='impersonate-start'),
)
