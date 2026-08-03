---
description: A named group of recipients within a Project, meant to receive one or more Notifications.
template: term.html
terms:
  - glossary:
      - Distribution List
---
# Distribution List

Named group of <glossary:Recipient|recipients> within a <glossary:Project>.
Each <glossary:Notification> references one **Distribution List** to determine
who receives the message when an <glossary:Event> is triggered.

A Distribution List contains zero or more <glossary:Assignment|assignments>
(a user's address on a specific <glossary:Channel>). It can be optionally
**pinned** to an <glossary:Application> — when pinned, the recipients
represent users of that specific application and the list can only be used
by Notifications whose Event belongs to the same Application.

!!! info "See also"
    [Admin Guide: Distribution Lists](../adm-guide/dl.md) |
    [API Reference](../api/distribution_lists.md)
