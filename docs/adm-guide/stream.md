---
tags:
   - Stream

---
# Stream

The Stream page shows the log messages produced by the Bitcaster applications in
real time. It is the first place to look when something goes wrong with an
<glossary:Event> or a dispatcher.

## Stream list

The list at <https://SERVER_ADDRESS/admin/bitcaster/logmessage/> shows every
message with:

- **created** — when the message was logged
- **level** — the log severity (`INFO`, `WARNING`, `ERROR`, ...)
- **application** — the application that produced the message

Filter by level or application to find what you are looking for.

The stream is **read-only**: messages are written by the system and cannot be
added or edited from the admin.
