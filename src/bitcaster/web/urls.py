# line too long
# flake8: noqa: E501
from django.conf import settings
from django.urls import include, path
from django.views.generic import TemplateView

from bitcaster.web.views.callbacks import confirm_address
from bitcaster.web.views.views import PreviewView

from .views import (ApplicationChannelCreate, ApplicationChannelDeprecate,
                    ApplicationChannelRemove, ApplicationChannels,
                    ApplicationChannelToggle, ApplicationChannelUpdate,
                    ApplicationCreate, ApplicationDashboard,
                    ApplicationUpdateView, EventCreate, EventDelete, EventList,
                    EventMessages, EventSubscriptions, EventSubscriptionsInvite,
                    EventSubscriptionsSubscribe, EventTest, EventToggle,
                    EventUpdate, IndexView, InviteAccept, InviteDelete,
                    InviteSend, LoginView, LogoutView, MessageCreate,
                    MessageDelete, MessageList, MessageUpdate,
                    OrganizationApplications, OrganizationChannelCreate,
                    OrganizationChannelDeprecate, OrganizationChannelRemove,
                    OrganizationChannels, OrganizationChannelToggle,
                    OrganizationChannelUpdate, OrganizationCreate,
                    OrganizationCreateMember, OrganizationDashboard,
                    OrganizationInvite, OrganizationMembers,
                    OrganizationTeamCreate, OrganizationTeamList,
                    OrganizationTeamMember, OrganizationTeamUpdate,
                    OrganizationUpdate, PluginInfo, SettingsChannelCreateWizard,
                    SettingsChannelDeleteView, SettingsChannelDeprecateView,
                    SettingsChannelListView, SettingsChannelToggleView,
                    SettingsChannelUpdateView, SettingsEmailView,
                    SettingsOAuthView, SettingsOrgListView,
                    SettingsOrgUpdateView, SettingsSystemInfo, SettingsView,
                    SetupView, SubscriptionList, UserAddressesView,
                    UserHomeView, UserProfileView, UserRegister,
                    UserWelcomeView, WorkInProgressView, confirm_registration,)

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
    path('settings/sysinfo/', SettingsSystemInfo.as_view(), name='settings-sysinfo'),
]

if not settings.ON_PREMISE:
    urlpatterns += [path('settings/organizations/', SettingsOrgListView.as_view(), name='settings-org-list'),
                    path('settings/organizations/<int:pk>/edit/', SettingsOrgUpdateView.as_view(),
                         name='settings-org-update'),
                    ]

urlpatterns += [
    path('settings/channel/', SettingsChannelListView.as_view(), name='settings-channels'),
    path('settings/channel/add/', SettingsChannelCreateWizard.as_view(), name='system-channel-create'),
    path('settings/channel/<int:pk>/edit/', SettingsChannelUpdateView.as_view(), name='system-channel-update'),
    path('settings/channel/<int:pk>/delete/', SettingsChannelDeleteView.as_view(), name='system-channel-delete'),
    path('settings/channel/<int:pk>/toggle/', SettingsChannelToggleView.as_view(), name='system-channel-toggle'),
    path('settings/channel/<int:pk>/deprecate/', SettingsChannelDeprecateView.as_view(),
         name='system-channel-deprecate'),
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

    path('new-user/', TemplateView.as_view(template_name='bitcaster/users/user_new.html')),
    path('new-association/', TemplateView.as_view(template_name='bitcaster/users/user_associated.html')),
    path('login-error/', TemplateView.as_view(template_name='bitcaster/users/login_error.html')),

    path('user/<slug:org>/', UserHomeView.as_view(), name='user-org'),
    path('user/<slug:org>/<slug:app>/', UserHomeView.as_view(), name='user-app'),

    # Applications
    path('<slug:org>/a/add/', ApplicationCreate.as_view(), name='application-create'),
    path('<slug:org>/a/<slug:app>/', ApplicationDashboard.as_view(), name='app-dashboard'),
    path('<slug:org>/a/<slug:app>/edit/', ApplicationUpdateView.as_view(), name='app-update'),
    path('<slug:org>/a/<slug:app>/subscriptions/', SubscriptionList.as_view(), name='app-subscriptions'),
    path('<slug:org>/a/<slug:app>/event/', EventList.as_view(), name='app-event-list'),
    path('<slug:org>/a/<slug:app>/event/add/', EventCreate.as_view(), name='app-event-create'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/edit/', EventUpdate.as_view(), name='app-event-update'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/toggle/', EventToggle.as_view(), name='app-event-toggle'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/test/', EventTest.as_view(), name='app-event-test'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/delete/', EventDelete.as_view(), name='app-event-delete'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/messages/', EventMessages.as_view(), name='app-event-messages'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/subscriptions/', EventSubscriptions.as_view(),
         name='app-event-subscriptions'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/subscriptions/subscribe/', EventSubscriptionsSubscribe.as_view(),
         name='app-event-subscriptions-subscribe'),
    path('<slug:org>/a/<slug:app>/event/<int:pk>/subscriptions/invite/', EventSubscriptionsInvite.as_view(),
         name='app-event-subscriptions-invite'),

    path('<slug:org>/a/<slug:app>/channel/', ApplicationChannels.as_view(), name='app-channel-list'),
    path('<slug:org>/a/<slug:app>/channel/add/', ApplicationChannelCreate.as_view(), name='app-channel-create'),
    path('<slug:org>/a/<slug:app>/channel/<int:pk>/edit/', ApplicationChannelUpdate.as_view(),
         name='app-channel-update'),
    path('<slug:org>/a/<slug:app>/channel/<int:pk>/delete/', ApplicationChannelRemove.as_view(),
         name='app-channel-delete'),
    path('<slug:org>/a/<slug:app>/channel/<int:pk>/toggle/', ApplicationChannelToggle.as_view(),
         name='app-channel-toggle'),
    path('<slug:org>/a/<slug:app>/channel/<int:pk>/deprecate/', ApplicationChannelDeprecate.as_view(),
         name='app-channel-deprecate'),

    path('o/<slug:org>/a/<slug:app>/message/', MessageList.as_view(), name='app-message-list'),
    path('o/<slug:org>/a/<slug:app>/message/add/', MessageCreate.as_view(), name='app-message-create'),
    path('o/<slug:org>/a/<slug:app>/message/<int:pk>/edit/', MessageUpdate.as_view(), name='app-message-update'),
    path('o/<slug:org>/a/<slug:app>/message/<int:pk>/delete/', MessageDelete.as_view(), name='app-message-delete'),

    # Organization
    path('org/add/', OrganizationCreate.as_view(), name='org-create'),
    path('<slug:org>/', OrganizationDashboard.as_view(), name='org-dashboard'),
    path('<slug:org>/update/', OrganizationUpdate.as_view(), name='org-config'),

    path('<slug:org>/member/', OrganizationMembers.as_view(), name='org-member-list'),
    path('<slug:org>/member/add/', OrganizationCreateMember.as_view(), name='org-member-register'),
    path('<slug:org>/user/<int:pk>/welcome/', UserWelcomeView.as_view(), name='org-member-welcome'),
    path('<slug:org>/invite/accept/<int:pk>/<str:check>/', InviteAccept.as_view(), name='org-member-accept'),
    path('<slug:org>/invite/delete/<int:pk>/', InviteDelete.as_view(), name='org-member-delete'),
    path('<slug:org>/invite/send/<int:pk>/', InviteSend.as_view(), name='org-member-send'),
    path('<slug:org>/invite/', OrganizationInvite.as_view(), name='org-member-invite'),

    path('<slug:org>/team/', OrganizationTeamList.as_view(), name='org-team-list'),
    path('<slug:org>/team/add/', OrganizationTeamCreate.as_view(), name='org-team-create'),
    path('<slug:org>/team/<slug:slug>/', OrganizationTeamUpdate.as_view(), name='org-team-update'),
    path('<slug:org>/team/<slug:slug>/members/', OrganizationTeamMember.as_view(), name='org-team-member'),

    path('<slug:org>/channel/', OrganizationChannels.as_view(), name='org-channel-list'),
    path('<slug:org>/channel/add/', OrganizationChannelCreate.as_view(), name='org-channel-create'),
    path('<slug:org>/channel/<int:pk>/edit/', OrganizationChannelUpdate.as_view(), name='org-channel-update'),
    path('<slug:org>/channel/<int:pk>/delete/', OrganizationChannelRemove.as_view(), name='org-channel-delete'),
    path('<slug:org>/channel/<int:pk>/toggle/', OrganizationChannelToggle.as_view(), name='org-channel-toggle'),
    path('<slug:org>/channel/<int:pk>/deprecate/', OrganizationChannelDeprecate.as_view(),
         name='org-channel-deprecate'),
    path('<slug:org>/applications/', OrganizationApplications.as_view(), name='org-applications'),

    path('', IndexView.as_view(), name='index'),
    path('wip/', WorkInProgressView.as_view(), name='wip'),

    path('tpl/<str:path>', PreviewView.as_view(), name='wip'),

]
