# Notifications

## Concept

A Notification is the rule that connects an **Event** to a
**Distribution List**. When an Event is triggered, the system looks up all
active Notifications for that Event, resolves the recipients from each
Notification's Distribution List, and delivers the message via the configured
Channels.

The flow is:

```
Event Trigger → Occurrence → Notification → Distribution List → Recipients
```

The [Distribution List](dl.md) defines **who** receives the notification. The
Notification itself defines **when** (which Event), **how** (which Channel and
Message Templates), and optional **filters** (payload filtering, dynamic
recipient selection).

## Create Notification Rule

1. Select the event you want to configure in your [Events list page](<https://SERVER_ADDRESS/admin/bitcaster/event/>)
2. From the Event's detail page, click the `Notifications`{ .bc-tool-button .link } button
3. The Notifications page lists the existing rules for the event — each row
   shows the `Name`, `Event`, `Application`, `Policy` and `Active` columns.
   The **Policy** column shows the recipient routing strategy; see
   [Notification Policies](notification_policies.md) for the details of each
   policy.
   Click on `Add` to create a new rule.
4. On the Add page, the `General` tab contains the `Name`, `Event` and
   `Environments` fields. Type the name of the rule and select the
   <glossary:Event> that triggers it. Optionally restrict the rule to a set of
   environments.
5. Open the `Recipients filters` tab, select the <glossary:Distribution List>
   that should receive the information. Tick the `Active` checkbox and click
   on `Save and Continue`{ .bc-button }.

!!! info "Pinned Distribution Lists"
    If the selected Distribution List is pinned to an Application, the Event's
    Application must match. Otherwise, the form will display a validation error.

Now that your Notification is ready you can click on the `Messages`{ .bc-tool-button .link }
to [create notification message](message.md)

## Configure the Notification filter

The `Notification filter` tab defines when this notification should be
triggered. Type a YAML document whose values are JMESPath expressions matched
against the incoming event payload. Rules can be combined with the `AND`, `OR`
and `NOT` operators; when the payload does not match, the notification is
skipped.

```yaml
AND:
  - 'severity == "critical"'
  - 'status != "resolved"'
```

For example, the filter above triggers the notification only for payloads
whose `severity` value is `critical` and whose `status` value is not `resolved`.

## Add Extra context

The `Extra context` tab adds static variables that are available in the
message templates together with the payload provided by the sender. Enter a
JSON object with the values you want to expose:

```json
{"support_email": "support@example.com", "label": "Order service"}
```

The message templates of this notification can then use `{{ support_email }}`
and `{{ label }}` as any other context variable.
