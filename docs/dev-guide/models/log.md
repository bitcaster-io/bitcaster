# LogEntry

Audit trail of actions performed on model objects (additions, changes, deletions and system actions).

## Purpose

The LogEntry is a proxy of Django's `django.contrib.admin.models.LogEntry` (stored in the `django_admin_log` table) that extends it with an `OTHER` action flag (value 100) used for system-generated actions. Records are created when objects are created, modified or deleted, and by the manager's `log_system_action()` which logs actions as the system user via `log_actions()`. The action flag choices are replaced at instantiation time with Addition, Change, Deletion and Other.

## Connections

- `user` -> User (settings.AUTH_USER_MODEL, on_delete CASCADE, related_name `logentry_set`)
- `content_type` -> ContentType (on_delete SET_NULL, blank/null, related_name `logentry_set`)
- Reverse: `user.logentry_set` lists all actions performed by a user
- No unique constraints (ordering: -action_time)

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| action_time | DateTimeField | No | timezone.now | action time (editable=False) |
| user | ForeignKey(User) | No | None | user |
| content_type | ForeignKey(ContentType) | Yes | None | content type |
| object_id | TextField | Yes | None | object id |
| object_repr | CharField(200) | No | None | object repr |
| action_flag | PositiveSmallIntegerField | No | None | action flag. Options: `1` Addition, `2` Change, `3` Deletion, `100` Other |
| change_message | TextField | No | "" | change message (string or JSON structure) |
