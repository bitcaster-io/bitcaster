from typing import TYPE_CHECKING

from collections.abc import Callable

from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from django.http import HttpRequest

# see https://fonts.google.com/icons?icon.query=docs for icons
COMMON_SITE_DROPDOWN = [
    {
        "icon": "inbox",
        "title": "Console",
        "link": "/console/",
    },
    {
        "icon": "home",
        "title": "Dashboard",
        "link": "/admin/",
    },
    {
        "icon": "webhook",
        "title": "API",
        "link": "/api/",
        "attrs": {
            "target": "_api",
        },
    },
    {
        "icon": "docs",
        "title": "Documentation",
        "link": "https://bitcaster-io.github.io/bitcaster/",
        "attrs": {
            "target": "_docs",
        },
    },
    {
        "icon": "mobile",
        "title": "Mobile",
        "link": "/pwa/",
        "attrs": {
            "target": "_mobile",
        },
    },
    {
        "icon": "commit",
        "title": "GitHub",
        "link": "https://github.com/bitcaster-io/bitcaster",
        "attrs": {
            "target": "_blank",
        },
    },
]

COMMON = {
    "LANGUAGES": {
        "navigation": [
            {"code": "en", "name_local": "English"},
            {"code": "es", "name_local": "Español"},
            {"code": "it", "name_local": "Italiano"},
        ],
    },
    "LOGIN": {
        "image": lambda request: static("bitcaster/images/logos/bitcaster.svg"),
        "redirect_after": lambda request: reverse_lazy("admin:index"),
    },
    "SHOW_LANGUAGES": True,
    "DASHBOARD_CALLBACK": "bitcaster.web.dashboard.home.callback.dashboard_callback",
    "ENVIRONMENT": "bitcaster.config.fragments.unfold.environment_callback",  # environment name in header
    "SHOW_HISTORY": True,
    "SITE_TITLE": "Bitcaster: ",
    "SITE_HEADER": "Bitcaster",
    "SITE_SUBHEADER": "",
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/x-icon",
            "href": lambda request: static("bitcaster/images/logos/logo400.png"),
        },
        {
            "rel": "icon",
            "sizes": "64x64",
            "type": "image/x-icon",
            "href": lambda request: static("bitcaster/images/logos/logo400.png"),
        },
    ],
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": lambda request: static("bitcaster/images/logos/logo400.png"),
        "dark": lambda request: static("bitcaster/images/logos/logo400.png"),
    },
    "COLORS": {
        "base": {
            "50": "249, 250, 251",
            "100": "243, 244, 246",
            "200": "229, 231, 235",
            "300": "209, 213, 219",
            "400": "156, 163, 175",
            "500": "107, 114, 128",
            "600": "75, 85, 99",
            "700": "55, 65, 81",
            "800": "31, 41, 55",
            "900": "17, 24, 39",
            "950": "3, 7, 18",
        },
        "primary": {
            "50": "254, 242, 242",
            "100": "254, 226, 226",
            "200": "254, 202, 202",
            "300": "252, 165, 165",
            "400": "248, 113, 113",
            "500": "239, 68, 68",
            "600": "220, 38, 38",
            "700": "185, 28, 28",
            "800": "153, 27, 27",
            "900": "127, 29, 29",
            "950": "69, 10, 10",
        },
    },
    "STYLES": [
        lambda *a: static("css/admin_ext.css"),
    ],
    "BORDER_RADIUS": "6px",
}


def has_model_permission(
    app_label: str = "bitcaster", model_name: str = "", codename: str = "view"
) -> Callable[..., bool]:
    return lambda request: request.user.is_superuser or request.user.has_perm(f"{app_label}.{codename}_{model_name}")


UNFOLD = {
    **COMMON,
    "SITE_TITLE": "Bitcaster Admin",
    "SITE_HEADER": "Bitcaster Admin",
    "SITE_DROPDOWN": [
        *COMMON_SITE_DROPDOWN,
    ],
    "SIDEBAR": {
        "show_search": True,  # Search in applications and models names
        "show_all_applications": lambda request: request.user.is_superuser,
        "navigation": [
            {
                "title": _("Monitor"),
                "separator": True,  # Top border
                "collapsible": False,  # Collapsible group of links
                "items": [
                    {
                        "title": _("Occurrences"),
                        "icon": "view_apps",
                        "link": reverse_lazy("admin:bitcaster_occurrence_changelist"),
                        "badge": "bitcaster.config.fragments.unfold.occurrence_callback",
                        "permission": has_model_permission(model_name="occurrence"),
                    },
                    {
                        "title": _("Deliveries"),
                        "icon": "task_alt",
                        "link": reverse_lazy("admin:bitcaster_delivery_changelist"),
                        "permission": has_model_permission(model_name="delivery"),
                    },
                    {
                        "title": _("Members"),
                        "icon": "person",
                        "link": reverse_lazy("admin:bitcaster_member_changelist"),
                        "permission": has_model_permission(model_name="member"),
                    },
                    {
                        "title": _("Stream"),
                        "icon": "call_log",
                        "link": reverse_lazy("admin:bitcaster_logmessage_changelist"),
                        "permission": has_model_permission(model_name="logmessage"),
                    },
                    {
                        "title": _("Messages"),
                        "icon": "inbox_text_person",
                        "link": reverse_lazy("admin:bitcaster_usermessage_changelist"),
                        "permission": has_model_permission(model_name="usermessage"),
                    },
                    {
                        "title": _("Attachments"),
                        "icon": "attachment",
                        "link": reverse_lazy("admin:bitcaster_attachment_changelist"),
                        "permission": has_model_permission(model_name="attachment"),
                    },
                ],
            },
            {
                "title": _("Configuration"),
                "separator": True,  # Top border
                "collapsible": False,  # Collapsible group of links
                "items": [
                    {
                        "title": _("Addresses"),
                        "icon": "alternate_email",
                        "link": reverse_lazy("admin:bitcaster_address_changelist"),
                        "permission": has_model_permission(model_name="address"),
                    },
                    {
                        "title": _("Distribution List"),
                        "icon": "patient_list",
                        "link": reverse_lazy("admin:bitcaster_distributionlist_changelist"),
                        "permission": has_model_permission(model_name="distributionlist"),
                    },
                    {
                        "title": _("Events"),
                        "icon": "event_list",
                        "link": reverse_lazy("admin:bitcaster_event_changelist"),
                        "permission": has_model_permission(model_name="event"),
                    },
                    {
                        "title": _("Notifications"),
                        "icon": "route",
                        "link": reverse_lazy("admin:bitcaster_notification_changelist"),
                        "permission": has_model_permission(model_name="notification"),
                    },
                    {
                        "title": _("Subscriptions"),
                        "icon": "subscriptions",
                        "link": reverse_lazy("admin:bitcaster_subscription_changelist"),
                        "permission": has_model_permission(model_name="subscription"),
                    },
                    {
                        "title": _("Message Templates"),
                        "icon": "article",
                        "link": reverse_lazy("admin:bitcaster_messagetemplate_changelist"),
                        "permission": has_model_permission(model_name="messagetemplate"),
                    },
                ],
            },
            {
                "title": _("Simulation"),
                "separator": True,  # Top border
                "collapsible": False,  # Collapsible group of links
                "items": [
                    {
                        "title": _("Event Simulations"),
                        "icon": "science",
                        "link": reverse_lazy("admin:bitcaster_eventsimulation_changelist"),
                        "permission": has_model_permission(model_name="eventsimulation"),
                    },
                    {
                        "title": _("Delivery Simulations"),
                        "icon": "task_alt",
                        "link": reverse_lazy("admin:bitcaster_deliverysimulation_changelist"),
                        "permission": has_model_permission(model_name="deliverysimulation"),
                    },
                ],
            },
            {
                "title": _("System"),
                "separator": True,  # Top border
                "collapsible": False,  # Collapsible group of links
                "items": [
                    {
                        "title": _("Channels"),
                        "icon": "business_messages",
                        "link": reverse_lazy("admin:bitcaster_channel_changelist"),
                        "permission": has_model_permission(model_name="channel"),
                    },
                    {
                        "title": _("Applications"),
                        "icon": "view_apps",
                        "link": reverse_lazy("admin:bitcaster_application_changelist"),
                        "permission": has_model_permission(model_name="application"),
                    },
                    {
                        "title": _("Memberships"),
                        "icon": "view_apps",
                        "link": reverse_lazy("admin:bitcaster_applicationmembership_changelist"),
                        "permission": has_model_permission(model_name="applicationmembership"),
                    },
                    {
                        "title": _("Projects"),
                        "icon": "view_apps",
                        "link": reverse_lazy("admin:bitcaster_project_changelist"),
                        "permission": has_model_permission(model_name="project"),
                    },
                    {
                        "title": _("Organization"),
                        "icon": "view_apps",
                        "link": reverse_lazy("admin:bitcaster_organization_changelist"),
                        "permission": has_model_permission(model_name="organization"),
                    },
                ],
            },
            {
                "title": _("Security"),
                "separator": True,  # Top border
                "collapsible": True,  # Collapsible group of links
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "person",
                        "link": reverse_lazy("admin:bitcaster_user_changelist"),
                        "permission": has_model_permission(model_name="user"),
                    },
                    {
                        "title": _("Roles"),
                        "icon": "account_child_invert",
                        "link": reverse_lazy("admin:bitcaster_userrole_changelist"),
                        "permission": has_model_permission(model_name="userrole"),
                    },
                    {
                        "title": _("Groups"),
                        "icon": "group",
                        "link": reverse_lazy("admin:bitcaster_group_changelist"),
                        "permission": has_model_permission(app_label="auth", model_name="group"),
                    },
                    {
                        "title": _("API Keys"),
                        "icon": "key",
                        "link": reverse_lazy("admin:bitcaster_apikey_changelist"),
                        "permission": has_model_permission(model_name="apikey"),
                    },
                    {
                        "title": _("System Log"),
                        "icon": "data_alert",
                        "link": reverse_lazy("admin:bitcaster_logentry_changelist"),
                        "permission": has_model_permission(app_label="admin", model_name="logentry"),
                    },
                    {
                        "title": _("SSO Providers"),
                        "icon": "captive_portal",
                        "link": reverse_lazy("admin:social_socialprovider_changelist"),
                        "permission": has_model_permission(app_label="social", model_name="socialprovider"),
                    },
                ],
            },
        ],
    },
    "TABS": [
        {
            "models": [
                "bitcaster.user",
            ],
            "items": [
                {
                    "title": _("Groups"),
                    "link": reverse_lazy("admin:auth_group_changelist"),
                },
            ],
        },
        {
            "models": [
                "auth.group",
            ],
            "items": [
                {
                    "title": _("Users"),
                    "link": reverse_lazy("admin:bitcaster_user_changelist"),
                },
            ],
        },
    ],
}


def environment_callback(request: "HttpRequest") -> tuple[str, str]:
    return settings.ENVIRONMENT, "info"


def occurrence_callback(request: "HttpRequest") -> int:
    from bitcaster.models import Occurrence

    return Occurrence.objects.filter(status=Occurrence.Status.NEW.value).count()
