# Organization

The `Organization` is the top-level tenant scope of the platform that owns users, projects, and default email settings.

## Purpose

An organization is the root of the data hierarchy; every project, application, event, and message template is scoped under one organization. At most two organizations can exist (the built-in "OS4D" one plus one local organization), enforced in `save()`, and records are created during initial setup or via the admin. It provides the organization-wide defaults for `from_email` and `subject_prefix`, exposes `enroll_users()` to bulk-create `UserRole` records for a group, and its `users` property resolves every user with a `UserRole` in it.

## Connections

- `owner` -> User (on_delete=PROTECT, related_name="managed_organizations")
- Reverse: `projects` -> Project (Organization.project, related_name="projects"), `userrole_set` -> UserRole, `channel_set` -> Channel, `messagetemplate_set` -> MessageTemplate
- Constraints: unique `slug` (`org_slug_unique`); unique `slug` + `owner` (`owner_slug_unique`)

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| from_email | EmailField | No (blank) | "" | default from address for emails |
| subject_prefix | CharField(max_length=50) | No | "[Bitcaster] " | Default prefix for messages supporting subject |
| owner | ForeignKey(User) | No | - | owner of the organization |
| name | CharField(max_length=255) from SlugMixin | No | - | name |
| slug | SlugField(max_length=255) from SlugMixin | No (blank) | - | record slug |
| version | IntegerVersionField from BitcasterBaseModel | No | 0 | version number of the record |
| last_updated | DateTimeField (auto_now) from BitcasterBaseModel | No | auto | Record last update time |
| created | DateTimeField (auto_now_add) from BitcasterBaseModel | No | auto | Record creation time |
