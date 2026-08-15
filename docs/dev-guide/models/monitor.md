# Monitor

Watchdog that applies an agent to an event to detect changes and record the latest result.

## Purpose

A Monitor links an agent (a polymorphic strategy selected from the agent registry) to an event and stores the agent configuration, its working data and the latest execution result as JSON. Records are created when a user wants to watch an event for changes; `has_changes()` delegates the change detection to the agent. The `active` flag enables/disables the monitor and `async_result` holds the identifier of the last asynchronous execution.

## Connections

- `event` -> Event (on_delete=CASCADE, related_name="monitor_set")
- Reverse: `monitor_set` on Event (Monitor.event, related_name="%(class)s_set")
- No unique constraints

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| name | CharField(255) | no | - | name for this monitor |
| event | ForeignKey(Event) | no | - | Event |
| agent | StrategyField (Agent registry) | no | - | Agent to use |
| active | BooleanField | no | True | Enable/Disable monitor |
| config | JSONField | no | dict | monitor configuration (editable=False) |
| data | JSONField | no | dict | monitor daa (editable=False) |
| result | JSONField | no | dict | monitor last execution result (editable=False) |
| async_result | CharField(255) | no | "" | async_result (editable=False) |
