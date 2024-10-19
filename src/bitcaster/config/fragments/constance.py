from bitcaster.auth.constants import DEFAULT_GROUP_NAME

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"


CONSTANCE_ADDITIONAL_FIELDS = {
    "html_minify_select": [
        "bitfield.forms.BitFormField",
        {"initial": 0, "required": False, "choices": (("html", "HTML"), ("line", "NEWLINE"), ("space", "SPACES"))},
    ],
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
    "MINIFY_RESPONSE": (0, "select yes or no", "html_minify_select"),
    "MINIFY_IGNORE_PATH": (r"", "regex for ignored path", str),
    "SYSTEM_EMAIL_CHANNEL": ("", "System Email", "email_channel"),
    "NEW_USER_IS_STAFF": (False, "Set any new user as staff", bool),
    "NEW_USER_DEFAULT_GROUP": (DEFAULT_GROUP_NAME, "Group to assign to any new user", "group_select"),
    "OCCURRENCE_DEFAULT_RETENTION": (30, "Number of days of Occurrences retention", int),
}
