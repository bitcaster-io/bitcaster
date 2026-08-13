# Channel

A Channel is a configured delivery endpoint (dispatcher + protocol) available to an organization, optionally scoped to a project.

## Purpose

A Channel binds a dispatcher strategy (e.g. test, email, slack) to a protocol and carries the dispatcher configuration. It belongs to an organization and can be scoped to a project via a chained foreign key; the `save` method derives the protocol from the dispatcher. Channels can be organized hierarchically through a self-referential `parent` (also chained on the organization), locked or paused via LockMixin, and flagged as `preferred` (default channel for its protocol in its scope). The `owner` property returns the project when set, otherwise the organization, and `from_email` / `subject_prefix` fall back from project to organization. The manager offers `active()` (active and not locked). Unique constraints scope channel names and the preferred channel per protocol within organization/project.

## Connections

- `organization` -> Organization (on_delete=CASCADE, related_name="%(class)s_set" -> "channel_set")
- `project` -> Project (ChainedForeignKey on `organization`, on_delete=CASCADE, related_name="%(class)s_set" -> "channel_set", blank, null)
- `parent` -> Channel (self, ChainedForeignKey on `organization`, blank, null)
- Reverse: `messages` (MessageTemplate.channel, related_name="messages")
- Reverse: `deliveries` (Delivery.channel, related_name="deliveries")
- Reverse: `event_set` (via Event.channels ManyToManyField, auto-generated accessor)
- Unique constraints: (`organization`, `name`) where project is null, (`organization`, `project`, `name`), (`organization`, `protocol`) where preferred and project is null, (`organization`, `project`, `protocol`) where preferred

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| locked | BooleanField | no | False | If checked any notification is ignored and not forwarded (inherited from LockMixin) |
| paused | BooleanField | no | False | If checked any notification paused (inherited from LockMixin) |
| organization | ForeignKey(Organization) | no | blank | Chanel organization |
| project | ChainedForeignKey(Project) | yes | null | project linked to this channel |
| name | CharField(255) | no | - | channel name |
| dispatcher | StrategyField | no | test | channel dispatcher (registry: dispatcherManager) |
| config | JSONField | no | dict | Channel configuration |
| protocol | CharField(50) | no | - | channel protocol: `PLAINTEXT`, `SLACK`, `SMS`, `EMAIL`, `WEBPUSH`, `INTERNAL`, `MARKDOWN` (set from dispatcher on save) |
| active | BooleanField | no | True | enable/disable channel |
| preferred | BooleanField | no | False | use this channel as default for its protocol in its scope |
| parent | ChainedForeignKey(Channel) | yes | null | parent channel |
| version | IntegerVersionField | no | - | version number of the record (inherited from BitcasterBaseModel) |
| last_updated | DateTimeField | no | auto | Record last update time (inherited from BitcasterBaseModel) |
| created | DateTimeField | no | auto | Record creation time (inherited from BitcasterBaseModel) |
