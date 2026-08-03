---
tags:
   - Task

---
# Schedule Tasks

Tasks let you run background jobs on a schedule: trigger an <glossary:Event>
periodically, purge old <glossary:Occurrence>s, refresh a monitor and so on.

## Task list

The list at <https://SERVER_ADDRESS/admin/bitcaster/task/> shows the name, the
function, the scheduling and whether the task is active.

## Add a task

1. Click **Add task**
1. Provide a **name** and a **slug**
1. Set **func** to the fully qualified name of the dramatiq actor to run
   (e.g. `bitcaster.runner.tasks.scan_occurrences`)
1. Optionally add **args** and **kwargs** passed to the function
1. Choose the **trigger** type and its configuration:
   - **interval** — run every N seconds/minutes/hours/days
   - **cron** — run according to a crontab expression
   - **date** — run once at a given time
1. Save

## Run and monitor

- **active** — enable or disable the task without deleting it
- **next run time** — when the task will run next (update it to reschedule)
- **replace existing** — replace a running instance with the same id
- **max instances** — maximum number of concurrent instances

Executions are recorded in the [Process Log](process_log.md).
