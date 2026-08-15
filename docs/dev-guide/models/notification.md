# Notification

A Notification defines which recipients are notified for an event, how they are selected, and which message templates apply.

## Purpose

Notifications are created per Event to describe one "subscription" rule: a routing policy, an optional distribution list, environment restrictions, a payload filter, and a recipients filter. On occurrence processing, valid notifications are matched against the event context (`match_filter`), pending assignments are collected via one of the policy-specific methods (`get_subscription_pending_subscriptions`, `get_dynamic_pending_subscriptions`, `get_distributionlist_pending_subscriptions`), and the resulting recipients are forwarded to the channel dispatchers. The `clean` method prevents a distribution list pinned to a different application. The policy field uses the global FILTERING choices, and the natural key is the name plus the event natural key.

## Connections

- `event` -> Event (on_delete=CASCADE, related_name="notifications")
- `distribution` -> DistributionList (on_delete=CASCADE, related_name="notifications", blank, null)
- Reverse: `messages` (MessageTemplate.notification, related_name="messages")
- Reverse: `deliveries` (Delivery.notification, related_name="deliveries")
- Reverse: `subscriptions` (Subscription.notification, related_name="subscriptions")
- Reverse: `simulation_deliveries` (DeliverySimulation.notification, related_name="simulation_deliveries")
- unique_together (`event`, `name`), also enforced by UniqueConstraint "notification_event_name"

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| name | CharField(100) | no | - | Notification name |
| description | TextField | yes | null | Small description of this notification |
| event | ForeignKey(Event) | no | - | Event linked to this notification |
| distribution | ForeignKey(DistributionList) | yes | null | Distribution to use for this notification. Can be empty depending on the policy |
| environments | ArrayField(CharField(20)) | yes | null | Allow notification only for these environments |
| policy | IntegerField | no | 1 | Routing policy: `1` No Filters. Forward to distribution list, `2` Direct subscriptions. Do not use DistributionList, forward to active Subscriptions, `3` API filters. Do not use DistributionList, filter users by API rules, `4` Filter users using provided rules. |
| extra_context | JSONField | no | dict | Extra context to add to what provided by the sender |
| active | BooleanField | no | False | If this notification is active |
| payload_filter | TextField | yes | null | YAML configuration to filter notifications based on event data. Use JMESPath expressions to match payload values. Supports logical operators (AND, OR, NOT). If the payload does not match the rules, the notification is skipped. |
| recipients_filter | JSONField | no | dict | JSON structure to dynamically select recipients. Use 'include' and 'exclude' keys with Django-style lookups (e.g., {'email__endswith': '@company.com'}). Supports nested lists for complex AND/OR logic. |
| version | IntegerVersionField | no | - | version number of the record (inherited from BitcasterBaseModel) |
| last_updated | DateTimeField | no | auto | Record last update time (inherited from BitcasterBaseModel) |
| created | DateTimeField | no | auto | Record creation time (inherited from BitcasterBaseModel) |
