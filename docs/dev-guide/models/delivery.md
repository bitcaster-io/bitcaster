# Delivery

A Delivery represents the sending of one message to one assignment for an occurrence, tracking status and retry information.

## Purpose

Delivery rows are created by `Occurrence._create_deliveries` for each (assignment, notification, channel) pair resolved during occurrence processing, with the rendered content stored in `data`. The `send` method builds the payload and hands it to the channel dispatcher, then marks the delivery as DELIVERED; `mark_error` increments the error counter and either schedules the next attempt (status ERROR, `next_attempt_at` = now + `DELIVERY_RETRY_DELAY` minutes) or marks the delivery as FAILURE once `MAX_DELIVERY_RETRIES` is reached. The `rendered` property exposes the rendered content from `data`, and `missing_template` is true when no message template was linked. A unique constraint prevents duplicate deliveries for the same occurrence/assignment/notification/channel combination.

## Connections

- `occurrence` -> Occurrence (on_delete=CASCADE, related_name="deliveries")
- `assignment` -> Assignment (on_delete=CASCADE, related_name="deliveries")
- `notification` -> Notification (on_delete=CASCADE, related_name="deliveries")
- `channel` -> Channel (on_delete=CASCADE, related_name="deliveries")
- `message_template` -> MessageTemplate (on_delete=CASCADE, related_name="deliveries", blank, null)
- Unique constraint on (`occurrence`, `assignment`, `notification`, `channel`), name "delivery_unique"
- Index on (`status`, `next_attempt_at`), name "delivery_status_next_attempt"

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| occurrence | ForeignKey(Occurrence) | no | - | Occurrence this delivery belongs to |
| assignment | ForeignKey(Assignment) | no | - | Assignment that receives the message |
| notification | ForeignKey(Notification) | no | - | Notification sent to the assignment |
| channel | ForeignKey(Channel) | no | - | Channel used to send the message |
| message_template | ForeignKey(MessageTemplate) | yes | null | Message template used for the delivery, if any |
| status | CharField(20) | no | PENDING | Status of the delivery: `PENDING` (Pending), `DELIVERED` (Delivered), `ERROR` (Error), `FAILURE` (Failure) |
| errors | IntegerField | no | 0 | Number of sending errors |
| next_attempt_at | DateTimeField | yes | null | Timestamp of the next allowed sending attempt. Null means due immediately |
| data | JSONField | no | dict | Information about the delivery (rendered content, errors) |
| version | IntegerVersionField | no | - | version number of the record (inherited from BitcasterBaseModel) |
| last_updated | DateTimeField | no | auto | Record last update time (inherited from BitcasterBaseModel) |
| created | DateTimeField | no | auto | Record creation time (inherited from BitcasterBaseModel) |
