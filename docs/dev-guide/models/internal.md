# LogMessage

Application-scoped log message entry produced by applications.

## Purpose

The LogMessage stores logging output bound to a single application: a logging level, the message body and the creation date. Records are created when an application emits a log message that must be tied to its application for later retrieval. The manager's `get_by_natural_key()` resolves records through the application chain (application slug, project slug, organization slug).

## Connections

- `application` -> Application (on_delete CASCADE, related_name `logmessage_set`)
- Reverse: `application.logmessage_set` lists all messages logged by an application
- No unique constraints

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| version | IntegerVersionField | No | None | version number of the record |
| last_updated | DateTimeField | No | None | Record last update time (auto_now) |
| created | DateTimeField | No | None | date of this message (auto_now_add) |
| level | CharField(255) | No | None | Log message level. Options (Python logging level names): `CRITICAL`, `FATAL`, `ERROR`, `WARNING`, `WARN`, `INFO`, `DEBUG`, `NOTSET` |
| message | TextField | No | None | message body |
| application | ForeignKey(Application) | No | None | application linked to this message |
