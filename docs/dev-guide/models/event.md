# Event

An Event is the entry point of the notification flow: triggering an event produces an Occurrence that is routed to recipients.

## Purpose

An Event groups notifications for a given application and is the object that senders trigger to start the notification process. Records are created by users to define what can be notified (name, slug, description) and how (enabled channels, retention policy, newsletter mode). When an Event is triggered (via the `trigger` method or the API trigger URL), an Occurrence is created with the provided context and options. Notifications and MessageTemplates hang off the Event and are matched against the occurrence context to select recipients. Events inherit `name` and `slug` from SlugMixin (slug is auto-generated from the name on save), `locked` and `paused` from LockMixin, and the base audit fields from BitcasterBaseModel. The manager `get_queryset` prefetches the application, project and organization. Records belonging to the internal Bitcaster organization cannot be deleted and cannot be locked (`can_be_locked`).

## Connections

- `application` -> Application (on_delete=CASCADE, related_name="events")
- `channels` -> Channel (ManyToManyField, blank)
- Reverse: `notifications` (Notification.event, related_name="notifications")
- Reverse: `messages` (MessageTemplate.event, related_name="messages")
- Reverse: `simulations` (EventSimulation.event, related_name="simulations")
- Reverse: `occurrence_set` (Occurrence.event, auto-generated accessor)
- Reverse: `event_set` (via `channels` ManyToManyField, auto-generated accessor)
- unique_together: (`name`, `application`) and (`slug`, `application`)

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| name | CharField(255) | no | - | name (inherited from SlugMixin) |
| slug | SlugField(255) | no | blank | record slug, auto-generated from name if empty (inherited from SlugMixin) |
| locked | BooleanField | no | False | If checked any notification is ignored and not forwarded (inherited from LockMixin) |
| paused | BooleanField | no | False | If checked any notification paused (inherited from LockMixin) |
| application | ForeignKey(Application) | no | - | application linked to this event |
| description | CharField(255) | yes | null | description of the event |
| active | BooleanField | no | True | enable/disable event notifications |
| newsletter | BooleanField | no | False | Do not customise notifications per single user |
| channels | ManyToManyField(Channel) | n/a | blank | list of channels enabled fot this event |
| occurrence_retention | IntegerField | yes | null | Number of days (from last update) after which related Occurrences can be purged. If not specified, system default will be used. |
| version | IntegerVersionField | no | - | version number of the record (inherited from BitcasterBaseModel) |
| last_updated | DateTimeField | no | auto | Record last update time (inherited from BitcasterBaseModel) |
| created | DateTimeField | no | auto | Record creation time (inherited from BitcasterBaseModel) |
