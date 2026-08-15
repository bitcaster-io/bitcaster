# Project

The `Project` groups applications under an organization and carries the lock state and email defaults for its scope.

## Purpose

A project is the second level of the hierarchy between `Organization` and `Application`, with a unique name and slug per organization. Records are created from the admin or by the `ScopedManager` helpers when an application or scoped object is created; `save()` defaults `owner` to the organization's owner when unset. The project inherits `LockMixin`, so locking or pausing it ignores or pauses notifications in its scope (`can_be_locked()` returns False only for the built-in "OS4D" organization), and it defines the list of available `environments` and the default `from_email`/`subject_prefix` used by its applications and messages.

## Connections

- `organization` -> Organization (on_delete=CASCADE, related_name="projects")
- `owner` -> User (on_delete=PROTECT, blank=True, no explicit related_name)
- Reverse: `applications` -> Application (Application.project, related_name="applications"), `channel_set` -> Channel (Channel.project ChainedForeignKey), `messagetemplate_set` -> MessageTemplate, `distributionlist_set` -> DistributionList, `apikey_set` -> ApiKey
- Unique together: (`organization`, `name`), (`organization`, `slug`)

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| organization | ForeignKey(Organization) | No | - | Organization |
| owner | ForeignKey(User) | No (blank) | - | Owner |
| from_email | EmailField | No (blank) | "" | default from address for emails |
| subject_prefix | CharField(max_length=50) | No | "[Bitcaster] " | Default prefix for messages supporting subject |
| environments | ArrayField(CharField(max_length=20)) | Yes | - | Environments available for project |
| name | CharField(max_length=255) from SlugMixin | No | - | name |
| slug | SlugField(max_length=255) from SlugMixin | No (blank) | - | record slug |
| locked | BooleanField from LockMixin | No | False | If checked any notification is ignored and not forwarded |
| paused | BooleanField from LockMixin | No | False | If checked any notification paused |
| version | IntegerVersionField from BitcasterBaseModel | No | 0 | version number of the record |
| last_updated | DateTimeField (auto_now) from BitcasterBaseModel | No | auto | Record last update time |
| created | DateTimeField (auto_now_add) from BitcasterBaseModel | No | auto | Record creation time |
