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
    USER_WRITE = "USER_WRITE", "User Write"
    # USER_ADMIN = "USER_ADMIN", "User Admin"
    #
    ORGANIZATION_READ = "ORG_READ", "Organization Read"
    # ORGANIZATION_WRITE = "ORG_WRITE", "Organization Write"
    # ORGANIZATION_ADMIN = "ORG_ADMIN", "Organization Admin"
    #
    # PROJECT_READ = "PROJECT_READ", "Project Read"
    # PROJECT_WRITE = "PROJECT_WRITE", "Project Write"
    # PROJECT_ADMIN = "PROJECT_ADMIN", "Project Admin"
    # PROJECT_LOCKOUT = "PROJECT_LOCKOUT", "Project Lockout"
    #
    # APPLICATION_READ = "APP_READ", "Application Read"
    # APPLICATION_WRITE = "APP_WRITE", "Application Write"
    APPLICATION_ADMIN = "APPLICATION_ADMIN", "Application Admin"
    # APPLICATION_LOCKOUT = "APP_LOCKOUT", "Application Lockout"
    #
    # EVENT_ADMIN = "EVENT_ADMIN", "Event Admin"
    # EVENT_READ = "EVENT_READ", "Event Read"
    EVENT_LIST = "EVENT_LIST", "Event list"
    EVENT_TRIGGER = "EVENT_TRIGGER", "Event Trigger"

    DISTRIBUTION_LIST = "DISTRIBUTION_LIST", "Distribution list"
    # EVENT_LOCKOUT = "EVENT_LOCKOUT", "Event Lockout"

    # MESSAGE_READ = "MESSAGE_READ", "Message Read"
    # MESSAGE_WRITE = "MESSAGE_WRITE", "Message Write"
    # MESSAGE_ADMIN = "MESSAGE_ADMIN", "Message Admin"
    #
    # CHANNEL_READ = "CHANNEL_READ", "Channel Read"
    # CHANNEL_WRITE = "CHANNEL_WRITE", "Channel Write"
    # CHANNEL_ADMIN = "CHANNEL_ADMIN", "Channel Admin"
    # CHANNEL_LOCKOUT = "CHANNEL_LOCKOUT", "Channel Lockout"
