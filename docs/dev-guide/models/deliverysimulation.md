# DeliverySimulation

A DeliverySimulation is the simulated equivalent of a Delivery: one previewed message for one assignment inside an EventSimulation.

## Purpose

DeliverySimulation rows are created by `EventSimulation.save_deliveries` for each (assignment, notification) pair collected during the simulation, storing the rendered preview (subject, message, html_message) in `data`. Unlike Delivery there is no channel link: the simulated message template implies the channel. Status uses the same choices as Occurrence.Status and defaults to NEW. The `rendered` and `missing_template` properties mirror those of Delivery. A unique constraint prevents duplicate rows for the same simulation/assignment/notification combination.

## Connections

- `simulation` -> EventSimulation (on_delete=CASCADE, related_name="deliveries")
- `assignment` -> Assignment (on_delete=CASCADE, related_name="simulation_deliveries")
- `notification` -> Notification (on_delete=CASCADE, related_name="simulation_deliveries")
- `message_template` -> MessageTemplate (on_delete=CASCADE, related_name="simulation_deliveries", blank, null)
- Unique constraint on (`simulation`, `assignment`, `notification`), name "delivery_simulation_unique"
- Index on (`simulation`, `notification`), name "delivery_simulation_sim_notif"

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| simulation | ForeignKey(EventSimulation) | no | - | Simulation this delivery belongs to |
| assignment | ForeignKey(Assignment) | no | - | Assignment reached by this delivery |
| notification | ForeignKey(Notification) | no | - | Notification sent to the assignment |
| message_template | ForeignKey(MessageTemplate) | yes | null | Message template used for the delivery, if any |
| status | CharField(20) | no | NEW | Status of the delivery: `NEW` (New), `PROCESSED` (Processing), `COMPLETED` (Completed), `FAILED` (Failed) |
| data | JSONField | no | dict | Information about the delivery (rendered content, errors) |
| version | IntegerVersionField | no | - | version number of the record (inherited from BitcasterBaseModel) |
| last_updated | DateTimeField | no | auto | Record last update time (inherited from BitcasterBaseModel) |
| created | DateTimeField | no | auto | Record creation time (inherited from BitcasterBaseModel) |
