# Distribution Lists

## Overview

A **Distribution List** is a named group of recipients within a Project.
It serves as the target audience for [Notifications](notification.md) — when an
Event triggers a Notification, the recipients are resolved from the
Notification's assigned Distribution List.

A Distribution List belongs to a Project and contains zero or more recipients
(an Assignment representing a user's address on a specific Channel).

## Purpose

Distribution Lists decouple **who receives a notification** from **what event
triggers it**. Multiple Notifications can share the same Distribution List,
and the same user can belong to multiple Distribution Lists.

Typical use cases:

- **Team alerts**: a Distribution List named "on-call-engineers" receives
  infrastructure alerts.
- **Customer communications**: a Distribution List named "active-users" receives
  product updates.
- **Cross-project lists**: a Distribution List can aggregate users from
  different Channels (email, Slack, SMS) into a single target.

## Link with Notifications

A [Notification](notification.md) is the rule that connects an Event to a
Distribution List. The flow is:

```
  Event Trigger → Occurrence → Notification → Distribution List → Recipients (Assignments)
```

- The **Event** defines **what** happened.
- The **Notification** defines **who** should know (via its Distribution List)
  and **how** (via Channels and Message Templates).
- The **Distribution List** defines the actual recipients.

Notifications with the default **No Filters** [Notification Policy](notification_policies.md)
require a Distribution List. Other policies (`subscription`, `external`,
`dynamic`) select recipients without using a Distribution List.

## Pinned Distribution List

A Distribution List can be optionally pinned to an Application by setting the
**Application** field. When pinned, each recipient in the list represents a user
in that application. This is useful in distributed environments where users are
managed externally.

### Motivation

In a distributed setup, users may exist across multiple applications, or some
applications (e.g. shell scripts) may have no users at all. A user can be added
to a Distribution List for an Event triggered by an Application that does not
own that user.

However, when a user is removed from an Application, they should stop receiving
notifications from Events triggered by that Application. Pinning a
Distribution List to an Application solves this: the remote application calls
the `unsubscribe` endpoint, and Bitcaster automatically removes the user from
all Distribution Lists pinned to that application.

### Behaviour

- **Pinned** (`application` is set): the Distribution List only works with
  Notifications whose Event belongs to the same Application. Creating or
  updating a Notification with a mismatched Application raises a validation
  error.
- **Non-pinned** (`application` is null): the Distribution List works as
  before with any Notification in the same Project.

### API Reference

- `POST /api/o/{org}/p/{prj}/a/{app}/unsubscribe/{username}/` — Removes a user
  from all Distribution Lists pinned to the application. Requires the new
  `MANAGE_APPLICATION_USERS` grant.

## Creating a Distribution List

From the [Project page](https://SERVER_ADDRESS/admin/bitcaster/project/current/){:target=_bc}
click on `Add Distribution List`{ .bc-tool-button .action }

The form contains a `Name` field, an optional `Application` selector to pin
the list, and the `Save` button.

Enter a name and optionally pin it to an Application. After saving, you can add
recipients via the `Recipients` button.

## Managing Recipients from the Member Page

Recipients can also be added from a Member's admin page. Open any
[Member](user_management.md) in the admin and switch to the
**Distribution Lists** tab. The tab shows two columns per row:

- **Distribution List**: the list the member belongs to.
- **Assignment**: the member's assignment (`address - channel`) used to reach
  them in that list.

Existing memberships are shown as pre-selected, read-only rows — the tab does
**not** create, edit, or delete Distribution Lists.

To add the member to another list, use the empty row at the bottom: pick an
existing Distribution List from the dropdown (lists the member is already in
are hidden) and choose one of the member's Assignments. On save, the member
receives the notification on that channel for the chosen list. Adding a member
who is already in the list is a no-op.
