---
tags:
   - Subscription

---
# Manage Subscriptions

A Subscription lets a user listen to a <glossary:Notification> directly, without
being part of any <glossary:Distribution List>.

The user is derived from the address of the subscribed
<glossary:Assignment>, so the assignment must exist and be active on the
channel the notification is delivered on.

Subscriptions are the recipient source for notifications using the
**Direct subscriptions** [Notification Policy](notification_policies.md).

## Subscription list

The list at <https://SERVER_ADDRESS/admin/bitcaster/subscription/> shows every
subscription with its notification, the assignment used to receive it and
whether it is active.

## Add or edit a subscription

1. Select the **notification** the user wants to listen to
1. Select the **assignment** that carries the address that will receive the message
1. Keep **active** checked to enable the subscription

Disable the **active** flag (or delete the subscription) to stop the user from
receiving that notification.
