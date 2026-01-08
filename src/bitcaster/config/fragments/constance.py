from bitcaster.auth.constants import DEFAULT_GROUP_NAME

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
    "OCCURRENCE_DEFAULT_RETENTION": (30, "Number of days of Occurrences retention", int),
}
