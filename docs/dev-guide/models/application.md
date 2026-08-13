# Application

The `Application` is the unit of notification delivery under a project, defining events, channels scope, and auto-creation behavior.

## Purpose

An application belongs to a project (with unique name and slug per project) and collects the events, attachments, API keys, message templates, and user memberships for a single product or service. Records are created via the admin, the API, or `ApplicationManager.get_or_create()` helpers; `save()` defaults `owner` to the project's owner when unset. Applications inherit `LockMixin` (locks are allowed outside the built-in "OS4D" organization) and control the notification flow through `active`, `auto_create_event`, and `auto_create_options`: unknown events received can be created and processed, created inactive, created paused, or created without triggering. `register_event()` and `create_message()` are the programmatic entry points for events and message templates.

## Connections

- `project` -> Project (on_delete=CASCADE, related_name="applications")
- `owner` -> User (on_delete=PROTECT, related_name="applications", blank=True)
- Reverse: `events` -> Event (Event.application, related_name="events"), `memberships` -> ApplicationMembership (related_name="memberships"), `attachments` -> Attachment (related_name="attachments"), `messagetemplate_set` -> MessageTemplate, `apikey_set` -> ApiKey, `distributionlist_set` -> DistributionList (application ChainedForeignKey)
- Unique together: (`project`, `name`), (`project`, `slug`)

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| project | ForeignKey(Project) | No | - | project this application belong to |
| owner | ForeignKey(User) | No (blank) | - | owner of this application |
| active | BooleanField | No | True | Whether the application should be active |
| auto_create_event | BooleanField | No | False | If true unknown events will be automatically created |
| auto_create_options | IntegerField (AutoCreateOption.choices) | No | PROCESS (100) | Options for automatically created events: PROCESS (100) "Create eevent and process", INACTIVE (10) "Create eevent and set it not active", PAUSED (20) "Create eevent and set it paused", DUMMY (30) "Create event but do not trigger it" |
| from_email | EmailField | No (blank) | "" | default from address for emails |
| subject_prefix | CharField(max_length=50) | No | "[Bitcaster] " | Default prefix for messages supporting subject |
| advanced_configuration | JSONField | Yes (blank) | {} | Advanced configuration, i.e. for attachment support |
| name | CharField(max_length=255) from SlugMixin | No | - | name |
| slug | SlugField(max_length=255) from SlugMixin | No (blank) | - | record slug |
| locked | BooleanField from LockMixin | No | False | If checked any notification is ignored and not forwarded |
| paused | BooleanField from LockMixin | No | False | If checked any notification paused |
| version | IntegerVersionField from BitcasterBaseModel | No | 0 | version number of the record |
| last_updated | DateTimeField (auto_now) from BitcasterBaseModel | No | auto | Record last update time |
| created | DateTimeField (auto_now_add) from BitcasterBaseModel | No | auto | Record creation time |
