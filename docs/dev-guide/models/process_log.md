# ProcessLogEntry

Execution record for a background task processed by the worker.

## Purpose

The ProcessLogEntry logs every run of an actor function: success or failure status, elapsed time, the task name and fully-qualified function path, the arguments passed (with secrets masked before storage), and the exception info on error. Records are created by the manager's `log_process()` method after each task execution. `exc_info` is empty on success.

## Connections

- No ForeignKey fields
- No reverse relations
- No unique constraints

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| action_time | DateTimeField | No | timezone.now | Action time (editable=False) |
| status | IntegerField | No | 10 | Status. Options: `10` Success, `20` Failure |
| elapsed | IntegerField | Yes | None | Elapsed time |
| task_name | CharField(100) | Yes | None | Task name |
| task_func | CharField(500) | Yes | None | Task full path |
| args | JSONField | Yes | None | Task arguments |
| kwargs | JSONField | Yes | None | Task keyword arguments |
| exc_info | TextField | Yes | "" | Exception info |
