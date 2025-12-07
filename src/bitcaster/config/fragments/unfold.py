from django.conf import settings
from django.http import HttpRequest
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

COMMON = {
    "LOGIN": {
        "image": lambda request: static("bitcaster/images/logos/logo400.png"),
        "redirect_after": lambda request: reverse_lazy("admin:index"),
    },
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
    "SITE_SYMBOL": "speed",  # symbol from icon set
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": lambda request: static("bitcaster/images/logos/logo400.png"),
        "dark": lambda request: static("bitcaster/images/logos/logo400.png"),
    },
    "COLORS": {
        "base": {
            "50": "249, 250, 251",  # grigi chiari (default neutral)
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
    "STYLES": [],
    "BORDER_RADIUS": "6px",
}

UNFOLD = {
    **COMMON,
    "SITE_TITLE": "Bitcaster Admin",
    "SITE_HEADER": "Bitcaster Admin",
    "SITE_DROPDOWN": [
        {
            "icon": "diamond",
            "title": "Console",
            "link": "/console/",
        },
        {
            "icon": "diamond",
            "title": "GitHub",
            "link": "https://github.com/bitcaster-io/bitcaster",
        },
        {
            "icon": "diamond",
            "title": "Documentation",
            "link": "https://bitcaster-io.github.io/bitcaster/",
        },
        # ...
    ],
    # https://fonts.google.com/icons
    "__SIDEBAR": {
        "show_search": True,  # Search in applications and models names
        "show_all_applications": True,  # Dropdown with all applications and models
        "navigation": [
            {
                "title": "HOPE",
                "separator": True,  # Top border
                "collapsible": False,  # Collapsible group of links
                "items": [
                    {
                        "title": _("Programs"),
                        "icon": "folder",
                        "link": reverse_lazy("admin:hope_program_changelist"),
                    },
                    {
                        "title": _("Offices"),
                        "icon": "domain",
                        "link": reverse_lazy("admin:hope_businessarea_changelist"),
                    },
                    {
                        "title": _("Household"),
                        "icon": "people",
                        "link": reverse_lazy("admin:hope_household_changelist"),
                    },
                    {
                        "title": _("Individual"),
                        "icon": "person",
                        "link": reverse_lazy("admin:hope_individual_changelist"),
                    },
                    {
                        "title": _("Payment Plans"),
                        "icon": "assignment",
                        "link": reverse_lazy("admin:hope_paymentplan_changelist"),
                    },
                    {
                        "title": _("Payments"),
                        "icon": "payments",
                        "link": reverse_lazy("admin:hope_payment_changelist"),
                    },
                ],
            },
            {
                "title": _("Security"),
                "separator": True,  # Top border
                "collapsible": False,  # Collapsible group of links
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "person",
                        "link": reverse_lazy("admin:hope_portal_user_changelist"),
                    },
                    {
                        "title": _("Groups"),
                        "icon": "people",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
            {
                "title": _("Configuration"),
                "separator": True,  # Top border
                "collapsible": False,  # Collapsible group of links
                "items": [
                    {
                        "title": _("Constance"),
                        "icon": "settings",
                        "link": reverse_lazy("admin:constance_config_changelist"),
                    },
                    {
                        "title": _("Flags"),
                        "icon": "done",
                        "link": reverse_lazy("admin:flags_flagstate_changelist"),
                    },
                ],
            },
        ],
    },
    "__TABS": [
        {
            "models": [
                "auth.group",
            ],
            "items": [
                {
                    "title": _("Users"),
                    "link": reverse_lazy("admin:hope_portal_user_changelist"),
                },
            ],
        },
        {
            "models": [
                "hope_live.user",
            ],
            "items": [
                {
                    "title": _("Groups"),
                    "link": reverse_lazy("admin:auth_group_changelist"),
                },
            ],
        },
    ],
}

CONSOLE = {
    **COMMON,
    "SITE_TITLE": "Bitcaster Console",
    "SITE_HEADER": "Bitcaster Console",
    "SITE_DROPDOWN": [
        {
            "icon": "diamond",
            "title": "Admin",
            "link": "/admin/",
        },
        {
            "icon": "diamond",
            "title": "GitHub",
            "link": "https://github.com/bitcaster-io/bitcaster",
        },
        {
            "icon": "diamond",
            "title": "Documentation",
            "link": "https://bitcaster-io.github.io/bitcaster/",
        },
        # ...
    ],
}

def badge_callback(request: HttpRequest) -> str:
    return ""


def environment_callback(request: "HttpRequest") -> tuple[str, str]:
    return settings.ENVIRONMENT, "info"
