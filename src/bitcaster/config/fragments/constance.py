from bitcaster.auth.constants import (
    DEFAULT_GROUP_NAME,
)
from bitcaster.constants import (
    DEFAULT_EVENT_SIMULATION_RETENTION,
    DEFAULT_OCCURRENCE_DEFAULT_RETENTION,
    DEFAULT_OCCURRENCE_MAX_RETENTION,
)

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"


CONSTANCE_ADDITIONAL_FIELDS = {
    "email": [
        "django.forms.EmailField",
        {},
    ],
    "email_channel": [
        "bitcaster.utils.constance.EmailChannel",
        {},
    ],
    "group_select": [
        "bitcaster.utils.constance.GroupSelect",
        {"initial": DEFAULT_GROUP_NAME},
    ],
}

CONSTANCE_CONFIG = {
    "SYSTEM_EMAIL_CHANNEL": ("", "System Email", "email_channel"),
    "NEW_USER_IS_STAFF": (False, "Set any new user as staff", bool),
    "NEW_USER_DEFAULT_GROUP": (DEFAULT_GROUP_NAME, "Group to assign to any new user", "group_select"),
    "OCCURRENCE_DEFAULT_RETENTION": (
        DEFAULT_OCCURRENCE_DEFAULT_RETENTION,
        "Number of days of Occurrences retention",
        int,
    ),
    "OCCURRENCE_MAX_RETENTION": (
        DEFAULT_OCCURRENCE_MAX_RETENTION,
        "Maximum number of days of Occurrences retention",
        int,
    ),
    "DEBUG_PREVIEW_RENDER_LIMIT": (
        20,
        "Max recipients rendered per debug preview",
        int,
    ),
    "EVENT_SIMULATION_RETENTION": (
        DEFAULT_EVENT_SIMULATION_RETENTION,
        "Number of days of EventSimulation retention",
        int,
    ),
    "EVENT_SIMULATION_TIMEOUT": (
        10,
        "Minutes after which a RUNNING EventSimulation is considered timed out",
        int,
    ),
    "EVENT_SIMULATION_PAGE_SIZE": (
        100,
        "Number of delivery rows shown per page in an EventSimulation",
        int,
    ),
    "SECRET_KEY_SALT": ("", "Salt to use to generate secret keys", str),
    "SERVER_URL": ("", "The base URL for attachment file downloads (no trailing slash)", str),
    "SOCIAL_AUTH_CREATE_USER": (True, "If true, not existing users will be automatically created", bool),
    "SOCIAL_AUTH_ACCEPTED_USERS": ("", "comma separated list of usernames accepted ", str),
}
