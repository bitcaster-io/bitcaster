# EventSimulation

An EventSimulation records a dry-run of an event trigger and produces per-recipient DeliverySimulation previews.

## Purpose

EventSimulation represents a simulation run of an Event: it stores the sample context and options used, the simulation mode, and the processing status. A record is created when a user simulates an event; the `save_deliveries` method persists the per-recipient preview transcript returned by `Occurrence.preview` into DeliverySimulation rows and trims `data` down to an aggregate summary. The manager provides `purgeable` for rows older than the configured `EVENT_SIMULATION_RETENTION` retention (in days). Status uses the same choices as Occurrence.Status, and mode controls the depth of the simulation (`fast`, `full`, `partial`).

## Connections

- `event` -> Event (on_delete=CASCADE, related_name="simulations")
- `created_by` -> User (settings.AUTH_USER_MODEL, on_delete=CASCADE, auto-generated accessor)
- Reverse: `deliveries` (DeliverySimulation.simulation, related_name="deliveries")

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| event | ForeignKey(Event) | no | - | simulation event |
| created_by | ForeignKey(User) | no | - | user that created the simulation |
| context | JSONField | no | dict | Sample context used for the simulation |
| options | JSONField | no | dict | Options provided by the sender to route linked notifications |
| mode | CharField(20) | no | - | Depth of the simulation: `fast` (Fast), `full` (Full), `partial` (Partial) |
| status | CharField(20) | no | NEW | Status of the simulation: `NEW` (New), `PROCESSED` (Processing), `COMPLETED` (Completed), `FAILED` (Failed) |
| data | JSONField | no | dict | Information about the processing (recipients, channels) |
| timestamp | DateTimeField | no | auto | Timestamp when simulation has been created. |
| version | IntegerVersionField | no | - | version number of the record (inherited from BitcasterBaseModel) |
| last_updated | DateTimeField | no | auto | Record last update time (inherited from BitcasterBaseModel) |
| created | DateTimeField | no | auto | Record creation time (inherited from BitcasterBaseModel) |
