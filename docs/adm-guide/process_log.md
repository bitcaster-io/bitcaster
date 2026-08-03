---
tags:
   - Process

---
# Process Log

The Process Log page lists the executions of the background tasks (dramatiq
actors) that Bitcaster runs: processing occurrences, purging old records,
checking monitors and so on. It answers the question "did the background job
run and did it succeed?" without digging into the workers' logs.

## Process log list

The list at <https://SERVER_ADDRESS/admin/bitcaster/processlogentry/> shows for
each execution:

- **action time** — when the task ran
- **status** — whether it succeeded or failed
- **elapsed** — how long the task took
- **task name** — the actor that ran

Use the **Type** filter to show only the executions of a specific task.

The log is **read-only**: it is written by the background manager and cannot be
modified from the admin. Failed executions here are usually the first symptom
of a misconfigured task, channel or dispatcher.
