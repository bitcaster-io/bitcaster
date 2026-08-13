# User

The `User` is the platform's custom Django auth user that adds timezone/format preferences, custom fields, lock state, and optimistic concurrency to the stock `AbstractUser`.

## Purpose

A user is created at signup or via the admin and is the identity that owns organizations, projects, and applications, subscribes to applications through `ApplicationMembership`, receives addresses/assignments for channels, and holds API keys. It extends `AbstractUser` with a `timezone`, preferred date/time formats (both selectable from settings-derived choices), a `custom_fields` JSON blob, and `LockMixin` flags that pause or ignore notifications directed at the user. `natural_key()` is the username; `organizations` returns all organizations when superuser, otherwise those reached via `UserRole`.

## Connections

- `groups` -> Group (ManyToManyField, related_name="user_set", related_query_name="user", blank)
- `user_permissions` -> Permission (ManyToManyField, related_name="user_set", related_query_name="user", blank)
- Reverse: `managed_organizations` -> Organization (Organization.owner, PROTECT), `project_set` -> Project (Project.owner, PROTECT), `applications` -> Application (Application.owner, PROTECT), `memberships` -> ApplicationMembership (CASCADE), `roles` -> UserRole (CASCADE), `addresses` -> Address (CASCADE), `keys` -> ApiKey (CASCADE), `bitcaster_messages` -> UserMessage (CASCADE)
- Custom permissions: `console_lock` ("Can access Lock console"), `console_tools` ("Can access Tools console")

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| timezone | TimeZoneField | No | "UTC" | User time zone |
| date_time_format | CharField(max_length=50) | No | settings.DATETIME_FORMAT | User preferred date and time format (choices derived from settings.DATE_FORMATS and TIME_FORMATS) |
| date_format | CharField(max_length=50) | No | settings.DATE_FORMAT | User preferred date only format (choices derived from settings.DATE_FORMATS) |
| time_format | CharField(max_length=50) | No | settings.TIME_FORMATS | User time only format (choices derived from settings.TIME_FORMATS) |
| custom_fields | JSONField | No (blank) | {} | User custom fields |
| locked | BooleanField from LockMixin | No | False | If checked any notification is ignored and not forwarded |
| paused | BooleanField from LockMixin | No | False | If checked any notification paused |
| version | IntegerVersionField from BitcasterBaseModel | No | 0 | version number of the record |
| last_updated | DateTimeField (auto_now) from BitcasterBaseModel | No | auto | Record last update time |
| created | DateTimeField (auto_now_add) from BitcasterBaseModel | No | auto | Record creation time |
| id | BigAutoField (AbstractUser) | No | auto | primary key |
| password | CharField(max_length=128) (AbstractUser) | No | - | raw password, stored hashed |
| last_login | DateTimeField (AbstractUser) | Yes (blank) | - | last login timestamp |
| is_superuser | BooleanField (AbstractUser) | No | False | designates full admin privileges |
| username | CharField(max_length=150) (AbstractUser) | No | - | login identifier, unique |
| first_name | CharField(max_length=150) (AbstractUser) | No (blank) | - | first name |
| last_name | CharField(max_length=150) (AbstractUser) | No (blank) | - | last name |
| email | EmailField(max_length=254) (AbstractUser) | No (blank) | - | email address |
| is_staff | BooleanField (AbstractUser) | No | False | designates admin-site access |
| is_active | BooleanField (AbstractUser) | No | True | marks the account active |
| date_joined | DateTimeField (AbstractUser) | No | timezone.now | account creation timestamp |
