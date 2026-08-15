# Occurrence

An Occurrence is a single trigger of an Event, carrying the sender context and tracking the delivery of notifications to recipients.

## Purpose

Occurrence records are created by `Event.trigger` every time an event is fired, storing the sender-provided context, routing options, and a correlation id. The `process` method resolves valid notifications and channels, collects recipients through assignments, creates Delivery rows, and drives the status machine (NEW -> PROCESSING/PROCESSED, COMPLETED, FAILED) with a limited number of attempts; the `preview` method runs the same pipeline as a dry run. `recipients` holds the total number of reached recipients, and `data` accumulates information about the processing. The manager offers `purgeable`, based on the event `occurrence_retention` or the system default, and `system` to filter occurrences of the internal Bitcaster application. An occurrence can reference a parent occurrence (used for system-triggered events such as silence or error notifications).

## Connections

- `event` -> Event (on_delete=CASCADE, auto-generated accessor "occurrence_set")
- `parent` -> Occurrence (self, on_delete=CASCADE, blank, null, editable=False, auto-generated accessor for child occurrences)
- Reverse: `deliveries` (Delivery.occurrence, related_name="deliveries")
- Unique constraint on (`timestamp`, `event`), name "occurrence_unique"

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| timestamp | DateTimeField | no | auto | Timestamp when occurrence has been created. |
| event | ForeignKey(Event) | no | - | event this occurrence belongs to |
| context | JSONField | no | dict | Context provided by the sender |
| options | JSONField | no | dict | Options provided by the sender to route linked notifications |
| correlation_id | CharField(255) | yes | null | Correlation ID provided by the sender (editable=False) |
| recipients | IntegerField | no | 0 | Total number of reached recipients |
| newsletter | BooleanField | no | False | Do not customise notifications per single user |
| data | JSONField | no | dict | Information about the processing (recipients, channels) |
| status | CharField(20) | no | NEW | Status of the occurrence: `NEW` (New), `PROCESSED` (Processing), `COMPLETED` (Completed), `FAILED` (Failed) |
| attempts | IntegerField | no | 5 | The remaining number of attempts before the occurrence is marked as failed |
| parent | ForeignKey(self) | yes | null | parent occurrence, used for system-triggered events (editable=False) |
| version | IntegerVersionField | no | - | version number of the record (inherited from BitcasterBaseModel) |
| last_updated | DateTimeField | no | auto | Record last update time (inherited from BitcasterBaseModel) |
| created | DateTimeField | no | auto | Record creation time (inherited from BitcasterBaseModel) |
