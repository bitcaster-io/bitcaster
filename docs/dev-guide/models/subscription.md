# Subscription

A `Subscription` is a user's direct subscription to a `Notification`, allowing a user to listen to a notification without being member of any `DistributionList`.

## Purpose

The `Subscription` links a `Notification` to an `Assignment` (and therefore to the address of a user) so the user receives the notification directly. Records are created when a user opts in to a specific notification. The `user` is derived from the subscribed `Assignment`'s address (`assignment.address.user`). A subscription is only usable when the assignment's channel is enabled for the notification's event, exposed by the `is_valid` property; `validity` renders that state as an HTML badge. The `active` flag provides a soft on/off switch for the subscription.

## Connections

- `notification` -> `Notification` (on_delete=CASCADE, related_name="subscriptions")
- `assignment` -> `Assignment` (on_delete=CASCADE, related_name="subscriptions")
- Unique constraint: one record per (`notification`, `assignment`) pair (`bitcaster_subscription_notification_assignment`); `natural_key` is the primary key

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| notification | ForeignKey -> Notification | No | - | Notification the user wants to listen to |
| assignment | ForeignKey -> Assignment | No | - | Assignment used to receive the notification |
| active | BooleanField | No | True | If the subscription is active |
| version | IntegerVersionField | No | - | Version number of the record |
| last_updated | DateTimeField | No | - | Record last update time (auto_now) |
| created | DateTimeField | No | - | Record creation time (auto_now_add) |
