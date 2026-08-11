---
tags:
   - Console
   - Tools

---
# Console Tools

The console **Tools** section, reachable from the user menu at
<https://SERVER_ADDRESS/admin/bitcaster/user/toolsview>, groups a few
operational utilities for administrators.

## Clear cache

The **Clear cache** button removes all entries stored by Bitcaster in the
cache (message display/notify timestamps, sanity check reports and any other
cached data). The button shows the current number of cached keys.

## Sanity check

The **Run sanity check** button launches a background task that validates all
Subscriptions and <glossary:Distribution List>s to make sure they can be used
to deliver messages.

The task runs in background and stores its report in the cache. Once a report
exists, the button becomes a **View Sanity Check** link that leads to the
[results page](https://SERVER_ADDRESS/admin/bitcaster/user/sanityview).

### What is validated

For each **Subscription**:

- the subscription channel must be enabled for the notification event
  (`Assignment.channel` must be part of `Notification.event.channels`)
- a <glossary:Message> must exist for the channel and the event

For each **DistributionList**:

- distribution lists are only delivered through the <glossary:Notification>s
  linked to them (`notification.distribution`); for each linked active
  notification, every recipient <glossary:Assignment>'s channel must have a
  <glossary:Message> available for that channel and the notification's event
  (same lookup used at dispatch time)
- lists without any linked active notification are skipped: they cannot
  forward anything, so they are not a forwarding mis-configuration

For each **Event**:

- the event, its application and its project must not be locked, paused or
  deactivated
- at least one channel must be enabled for the event
- at least one active <glossary:Notification> must exist for the event
- every configured channel must be active, not locked/paused and have a valid
  dispatcher configuration
- a <glossary:Message> must exist for each configured channel and the event

### Results

The results page shows a summary per category (Subscriptions, Distribution
Lists, Events) and then groups the errors by the **missing or mis-configured
component** (e.g. `MessageTemplate`, `Channel`, `Event`). Each errored entry
shows its source, links to the affected object and offers a **Fix Issue** link.
For missing <glossary:Message> issues the link opens the "add MessageTemplate"
page with the form pre-filled with the relevant channel, event and
notification (for **Subscription** and
<glossary:Distribution List> issues), channel/event (for
<glossary:Event> issues), or channel/project when a stale report cannot
determine the event; other issues point to the affected object's page.

!!! note

    The report is stored in the cache and expires at midnight. Run the check
    again from the Tools page to refresh it.
