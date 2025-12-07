from typing import Any

from django.conf import settings
from django.http import HttpRequest
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# see https://fonts.google.com/icons?icon.query=docs for icons
COMMON_SITE_DROPDOWN = [
    {
        "icon": "commit",
        "title": "GitHub",
        "link": "https://github.com/bitcaster-io/bitcaster",
    },
    {
        "icon": "docs",
        "title": "Documentation",
        "link": "https://bitcaster-io.github.io/bitcaster/",
    },
]

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
    # "SITE_SYMBOL": "speed",  # symbol from icon set
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
            "icon": "apps",
            "title": "Console",
            "link": "/console/",
        },
        *COMMON_SITE_DROPDOWN,
    ],
    "SIDEBAR": {
        "show_search": True,  # Search in applications and models names
        "show_all_applications": True,  # Dropdown with all applications and models
    },
}

CONSOLE = {
    **COMMON,
    "SITE_TITLE": "Bitcaster Console",
    "SITE_HEADER": "Bitcaster Console",
    "SITE_DROPDOWN": [
        {
            "icon": "settings",
            "title": "Admin",
            "link": "/admin/",
        },
        *COMMON_SITE_DROPDOWN,
    ],
    "DASHBOARD_CALLBACK": "bitcaster.config.fragments.unfold.console_dashboard",
    "SIDEBAR": {
        "show_search": False,
        "command_search": False,
        "show_all_applications": False,  # Dropdown with all applications and models
        "navigation": [
            {
                "title": _("System"),
                "separator": True,  # Top border
                "collapsible": False,  # Collapsible group of links
                "items": [
                    {
                        "title": _("Address"),
                        "icon": "alternate_email",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("console:bitcaster_address_changelist"),
                        # "badge": "sample_app.badge_callback",
                        # "permission": lambda request: request.user.is_superuser,
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
                        "icon": "person",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("console:bitcaster_user_changelist"),
                        # "badge": "sample_app.badge_callback",
                        "permission": lambda request: request.user.is_superuser,
                    },
                    # {
                    #     "title": _("Users"),
                    #     "icon": "people",
                    #     "link": reverse_lazy("admin:auth_user_changelist"),
                    # },
                ],
            },
        ],
    },
}


def badge_callback(request: HttpRequest) -> str:
    return ""


def environment_callback(request: "HttpRequest") -> tuple[str, str]:
    return settings.ENVIRONMENT, "info"


def console_dashboard(request: "HttpRequest", context: dict[str, Any]) -> dict[str, Any]:
    context.update(
        {
            "sample": "example",  # this will be injected into templates/admin/index.html
        }
    )
    return context
