# MessageTemplate

A MessageTemplate holds the subject, text and HTML content used to render a message for a channel, optionally bound to an event and a notification.

## Purpose

MessageTemplates are the rendering artifacts of the platform: they are valid for a channel and optionally scoped to an event and/or a notification. A template with a notification set is only used for that notification; a template without one acts as a fallback for its event on the channel (`get_messages` prefers notification-bound templates). The `render` method produces subject, message and html_message according to the capabilities of the channel protocol, and injects debug information when `debug` is enabled. Records are created either manually or via `Event.create_message` / `Notification.create_message`. The model uses Scoped3Mixin so records are scoped to organization, project and application (all blank for organization-level templates, with project and application derived from the parent scope on save). The `clean` method forces the event to match the notification's event.

## Connections

- `organization` -> Organization (on_delete=CASCADE, related_name="%(class)s_set" -> "messagetemplate_set", blank; inherited from Scoped3Mixin)
- `project` -> Project (ChainedForeignKey on `organization`, on_delete=CASCADE, related_name="%(class)s_set" -> "messagetemplate_set", blank, null; inherited from Scoped3Mixin)
- `application` -> Application (ChainedForeignKey on `project`, on_delete=CASCADE, related_name="%(class)s_set" -> "messagetemplate_set", blank, null; inherited from Scoped3Mixin)
- `channel` -> Channel (on_delete=CASCADE, related_name="messages")
- `event` -> Event (on_delete=CASCADE, related_name="messages", blank, null)
- `notification` -> Notification (on_delete=CASCADE, related_name="messages", blank, null)
- Reverse: `deliveries` (Delivery.message_template, related_name="deliveries")
- Reverse: `simulation_deliveries` (DeliverySimulation.message_template, related_name="simulation_deliveries")
- Unique constraints: (`notification`, `channel`) "unique_message_for_notification", (`organization`, `project`, `name`) "unique_message_prj", (`organization`, `project`, `application`, `name`) "unique_message_app", (`organization`, `name`) "unique_message_org"

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| organization | ForeignKey(Organization) | no | blank | Organization (inherited from Scoped3Mixin) |
| project | ChainedForeignKey(Project) | yes | null | Project this record belong to (inherited from Scoped3Mixin) |
| application | ChainedForeignKey(Application) | yes | null | application (inherited from Scoped3Mixin) |
| name | CharField(255) | no | - | name of this template message |
| channel | ForeignKey(Channel) | no | - | Channel for which  the message is valid |
| event | ForeignKey(Event) | yes | null | Event to which this message belongs |
| notification | ForeignKey(Notification) | yes | null | Notification to which this message belongs |
| subject | TextField | yes | null | The subject of the message |
| content | TextField | no | blank | The content of the message |
| html_content | TextField | no | blank | The HTML formatted content of the message |
| debug | BooleanField | no | False | Allow debug information in the message |
| version | IntegerVersionField | no | - | version number of the record (inherited from BitcasterBaseModel) |
| last_updated | DateTimeField | no | auto | Record last update time (inherited from BitcasterBaseModel) |
| created | DateTimeField | no | auto | Record creation time (inherited from BitcasterBaseModel) |
