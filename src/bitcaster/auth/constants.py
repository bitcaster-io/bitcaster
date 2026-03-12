from django.db.models import TextChoices

DEFAULT_GROUP_NAME = "Default"


class Scope(TextChoices):
    ORGANIZATION = "ORGANIZATION", "ORGANIZATION"
    PROJECT = "PROJECT", "PROJECT"
    APPLICATION = "APPLICATION", "APPLICATION"


class Grant(TextChoices):
    FULL_ACCESS = "FULL_ACCESS", "Full Access"
    SYSTEM_PING = "SYSTEM_PING", "Ping"
    USER_READ = "USER_READ", "User Read"
    USER_PROFILE = "USER_PROFILE", "Read User Profile and emssages"
    USER_WRITE = "USER_WRITE", "User Write"

    ORGANIZATION_READ = "ORG_READ", "Organization Read"
    APPLICATION_ADMIN = "APPLICATION_ADMIN", "Application Admin"

    EVENT_LIST = "EVENT_LIST", "Event list"
    EVENT_TRIGGER = "EVENT_TRIGGER", "Event Trigger"
    EVENT_AUTO_CREATE = "EVENT_AUTO_CREATE", "Event Auto-Create"

    DISTRIBUTION_LIST = "DISTRIBUTION_LIST", "Distribution list"
