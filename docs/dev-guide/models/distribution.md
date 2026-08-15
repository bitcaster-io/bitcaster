# DistributionList

A `DistributionList` is a named, project-scoped collection of `Assignment` recipients that a `Notification` can be sent to.

## Purpose

The `DistributionList` groups recipient `Assignment`s under a name within a `Project`. Records are created when an operator wants to address a notification to a predefined set of recipients instead of individual addresses. When the `application` field is set, the list is pinned to that application (and `clean()` enforces the application belongs to the same project as the list); this pinning is later checked by `Notification` so that a notification's event application matches the distribution list's pinned application. `Notification.distribution` points to a `DistributionList`, and during dispatch the notification resolves pending subscriptions from `distribution.recipients`.

## Connections

- `project` -> `Project` (on_delete=CASCADE, no explicit related_name)
- `application` -> `Application` (ChainedForeignKey, chained on `project`, on_delete=SET_NULL, null=True, blank=True) - when set, the distribution list is pinned to this application
- `recipients` -> `Assignment` (ManyToManyField, blank=True, no explicit related_name; reverse on Assignment is `distributionlist_set`)
- Reverse: `notifications` -> `Notification` records whose `distribution` points here (on_delete=CASCADE, related_name="notifications" on `Notification.distribution`, null=True, blank=True)
- Unique together: (`name`, `project`); `natural_key` is (`name`, *`Project.natural_key()`)

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| name | CharField(255) | No | - | Name of this distribuition list (case-insensitive collation) |
| project | ForeignKey -> Project | No | - | Project linked to this distribution list |
| application | ChainedForeignKey -> Application | Yes | None | When set, the distribution list is pinned to this application |
| recipients | ManyToManyField -> Assignment | - | - | Members of the list |
| version | IntegerVersionField | No | - | Version number of the record |
| last_updated | DateTimeField | No | - | Record last update time (auto_now) |
| created | DateTimeField | No | - | Record creation time (auto_now_add) |
