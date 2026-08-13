# ApplicationMembership

The `ApplicationMembership` links a user to an application and controls whether that user receives notifications for it.

## Purpose

A membership is created when a user subscribes to an application (e.g. via the external register endpoint) and is unique per user/application pair. It carries the per-user delivery gating flags for that application: `locked` (admin-managed hard block), `active` (mirrors the client-side active state), and `enable_notifications` (soft opt-out); the `can_receive_notifications` property requires all three to be favorable. The manager's `blocked_user_ids()` returns the user ids for which the application must not send notifications, which is used by the notification flow to exclude them.

## Connections

- `user` -> User (on_delete=CASCADE, related_name="memberships")
- `application` -> Application (on_delete=CASCADE, related_name="memberships")
- Unique together: (`user`, `application`)

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| user | ForeignKey(User) | No | - | member user |
| application | ForeignKey(Application) | No | - | application the user is member of |
| custom_fields | JSONField | No (blank) | {} | Member custom fields for this application |
| locked | BooleanField | No | False | Managed only via the admin. If checked no notification is sent to the user for this application |
| active | BooleanField | No | True | Mirrors the client application 'active' state for the user. If unchecked the user receives no notifications for this application |
| enable_notifications | BooleanField | No | True | Whether the user receives notifications for this application (effective only when active and not locked) |
| version | IntegerVersionField from BitcasterBaseModel | No | 0 | version number of the record |
| last_updated | DateTimeField (auto_now) from BitcasterBaseModel | No | auto | Record last update time |
| created | DateTimeField (auto_now_add) from BitcasterBaseModel | No | auto | Record creation time |
