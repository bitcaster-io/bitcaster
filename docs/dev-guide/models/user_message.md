# UserMessage

Notification message delivered to a specific user's in-app inbox.

## Purpose

The UserMessage stores a message produced for a single user: subject, body, level and an optional event that generated it. Records are created by the message dispatcher when an event fires and the user's channel requires a in-site notification. Messages expire: the manager's `expired()` and `active()` filter records using a cutoff computed from the `message_ttl` setting (default 7 days) in the channel configuration of the user-message dispatcher. The `read` timestamp and `displayed` flag track user interaction.

## Connections

- `user` -> User (on_delete CASCADE, related_name `bitcaster_messages`)
- `event` -> Event (on_delete CASCADE, blank/null, related_name `usermessage_set`)
- Reverse: `user.bitcaster_messages` lists all messages of a user; `event.usermessage_set` lists the messages produced by an event
- No unique constraints

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| version | IntegerVersionField | No | None | version number of the record |
| last_updated | DateTimeField | No | None | Record last update time (auto_now) |
| created | DateTimeField | No | None | Message date (auto_now_add) |
| user | ForeignKey(User) | No | None | User |
| level | CharField(255) | No | INFO | Level of the message. Options (Python logging level names): `CRITICAL`, `FATAL`, `ERROR`, `WARNING`, `WARN`, `INFO`, `DEBUG`, `NOTSET` |
| subject | TextField | No | None | Subject of the message |
| message | TextField | No | None | Content of the message |
| event | ForeignKey(Event) | Yes | None | Event produced the message |
| read | DateTimeField | Yes | None | Read date |
| displayed | BooleanField | Yes | None | If the message has beed displayed to teh user |
