# Task

Definition of a scheduled periodic job executed by the Bitcaster scheduler.

## Purpose

A Task describes a recurring job: it references a function registered in the scheduler configuration (`func`), a trigger type with its configuration (interval or cron), the arguments to pass and whether the job is active. Records are created through the task administration UI. `save()` generates a UUID hex slug when the slug is empty. `get_job_args()` maps the record to the APScheduler job parameters and `scheduling()` renders a human-readable description of the trigger. `get_status()` returns "active" or "paused" based on the `active` flag. Tasks inherit the audit fields from BitcasterBaseModel.

## Connections

- No ForeignKey fields
- No reverse relations
- `slug` is unique; `name` is unique

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| version | IntegerVersionField | no | - | version number of the record (inherited from BitcasterBaseModel) |
| last_updated | DateTimeField | no | auto | Last updated (auto_now) |
| created | DateTimeField | no | auto | Record creation time (inherited from BitcasterBaseModel) |
| slug | SlugField(255) | no | - | Slug (unique; a UUID hex is generated on save when empty) |
| name | CharField(200) | no | - | Name (unique) |
| func | CharField(500) | no | - | Func (options dynamically generated from the scheduler configuration) |
| replace_existing | BooleanField | no | False | Replace existing |
| max_instances | IntegerField | no | 1 | Max instances (validators: min value 1) |
| next_run_time | DateTimeField | yes | - | Next run time |
| args | JSONField | no | list | Args |
| kwargs | JSONField | no | dict | Kwargs |
| trigger | CharField(500) | no | interval | Trigger. Options: `interval` Interval, `cron` Cron |
| trigger_config | JSONField | no | dict | Trigger config |
| active | BooleanField | no | False | Active |
