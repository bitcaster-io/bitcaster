# Member

The `Member` is a proxy model over `User` that exposes users through a recipient-oriented admin interface.

## Purpose

A `Member` is the same database row as a `User` (no extra fields or methods are defined); the proxy exists so the admin can manage platform users as "members" with their own verbose name (`Member`/`Members`) and dedicated admin configuration. Members are the notification recipients of the platform: they have addresses/assignments for channels and memberships that gate delivery per application.

## Connections

- Same connections as `User` (proxy model, no additional relations)
- `memberships` -> ApplicationMembership, `addresses` -> Address, `roles` -> UserRole, `managed_organizations` -> Organization, `applications` -> Application, `project_set` -> Project, `keys` -> ApiKey, `bitcaster_messages` -> UserMessage
- Custom permissions inherited from `User`: `console_lock`, `console_tools`

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| timezone | TimeZoneField | No | "UTC" | User time zone |
| date_time_format | CharField(max_length=50) | No | settings.DATETIME_FORMAT | User preferred date and time format |
| date_format | CharField(max_length=50) | No | settings.DATE_FORMAT | User preferred date only format |
| time_format | CharField(max_length=50) | No | settings.TIME_FORMATS | User time only format |
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
