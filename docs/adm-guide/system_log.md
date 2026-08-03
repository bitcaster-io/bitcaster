---
tags:
   - Log

---
# System Log

The System Log page shows the audit trail of every action performed in the
admin interface: who added, changed or deleted which object and when.

## System log list

The list at <https://SERVER_ADDRESS/admin/bitcaster/logentry/> shows for each
entry:

- **action time** — when the action was performed
- **user** — who performed it
- **content type** — the type of object affected
- **object** — the object that was added, changed or deleted
- **change message** — the summary of the change (e.g. changed fields)

The log is written automatically by Django and is **read-only**: entries cannot
be added or edited from the admin.

Use it to answer questions like "who changed this application last week?" or
"when was this channel deactivated?".
