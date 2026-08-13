# Quick Start

This guide shows how to configure Bitcaster end to end from a running web
interface: create the structure (Organization, Project), add a Channel, an
Application with its Event, a Notification with its Message Template,
subscribe a recipient and finally trigger a test Event to see the Delivery
reach its destination.

It assumes you have a running Bitcaster instance and you are already logged in.

## 1. Create the Organization and Project

### Organization

An **Organization** is the top-level tenant of Bitcaster, usually the company.
From the sidebar open **Organizations** and click `Add`{ .bc-tool-button .action }:

- `Name`: name of the organization.
- `From email`: default "from" address used for emails sent by this organization.
- `Subject Prefix`: default prefix prepended to the subject of messages that support one.
- `Owner`: user responsible for the organization.

!!! note

    You will find an already created `OS4D` Organization. It is used by
    Bitcaster itself: you cannot edit or delete it.

The Organization form contains the `Name`, `From email`, `Subject Prefix` and
`Owner` fields; the `Save` button is at the bottom of the form.

### Project

A **Project** groups the applications of a business unit, product line or
team. Click the `Create Project`{ .bc-tool-button .action } button in the top
right corner of the organization page, or open **Projects** in the sidebar and
click `Add`:

- `Name`: name of the project.
- `Organization`: parent organization (pre-filled when created from the organization page).
- `Owner`: user responsible for the project.
- `From Email`: default "from" address for emails sent under this project.
- `Subject Prefix`: default subject prefix for messages.
- `Environments`: comma-separated environments available for the project
  (e.g. `prod,staging`), used for environment-based notification routing.

The Project form shows the fields above; the organization is pre-filled when
the project is created from the organization page.

See [Create the Initial Structure](structure.md) for more details.

## 2. Create a Channel

A **Channel** is the transport Bitcaster uses to reach recipients (email,
SMS, Slack, ...) and is required by every later step.

From the [project page](structure.md) click `Add Channel`{ .bc-tool-button .action }:

- `Name`: name of the channel.
- `Dispatcher`: the protocol engine used to send messages (e.g. the *Email* dispatcher).
- `Configuration`: dispatcher-specific settings (e.g. SMTP server and
  credentials) as JSON.
- `Protocol`: derived from the dispatcher, read-only.
- `Active`: enable/disable the channel.

The Channel form contains the fields above; after saving, the dispatcher may
ask for extra provider-specific configuration.

You can also enable an Organization's
<glossary:Abstract Channel> instead of creating a new one — see
[Enable Project Channel](channel_enable.md).

## 3. Add the Application

An **Application** is the container of a single product or service: every
Event, Notification and API Key belongs to an Application.

From the sidebar open **Applications** and click `Add`{ .bc-tool-button .action }:

- `Name`: name of the application (the system that will trigger the events).
- `Project`: parent project (pre-filled when created from the project page).
- `Owner`: user responsible for the application.
- `Active`: whether the application accepts triggers.
- `Auto create events`: if enabled, unknown events are automatically created
  when they are triggered.
- `Auto create event options`: options applied to auto-created events.
- `From email`: default "from" address for emails.
- `Subject prefix`: default subject prefix for messages.
- `Advanced configuration`: JSON for advanced features (e.g. attachment support).

The Application form contains the fields above, grouped in sections such as
`General` and `Notification`; the `Save` button is at the bottom.

See [Add Application](app.md) for more details.

## 4. Register the Event

An **Event** is the entry point of Bitcaster: when it is triggered, Bitcaster
matches it against its active Notifications and delivers the messages.

From the application page click `Add Event`{ .bc-tool-button .action }:

- `Name`: name of the event (also used to build its trigger).
- `Description`: description of the event.
- `Active`: enable/disable notifications for this event.
- `Newsletter mode`: do not customise notifications per single user.
- `Channels`: the channels this event may use (select the channel created in
  step 2); recipients on other channels are ignored.
- `Occurrence retention`: how many days occurrences are kept before being
  purged (if empty the system default is used).

The Event form contains the fields above; the `Channels` field lets you pick
which of the project's channels this event may use.

After the event has been created, make sure the channel from step 2 is enabled
for it: open the event's detail page and check the `Channels` selection, then
save.

See [Register Application Events](events.md) for more details.

## 5. Create the Notification Rule

A **Notification** is the rule that connects an Event to its recipients.

From the event's detail page click `Notifications`{ .bc-tool-button .link }
and then `Add`:

The Notifications page lists the event's rules — with `Name`, `Event`,
`Application`, `Policy` and `Active` columns — and shows the `Add` button in
the top right corner. The Add form opens on the `General` tab.

- `Name`: name of the notification rule.
- `Description`: short description of the notification.
- `Event`: the linked event (pre-filled).
- `Distribution`: the distribution list used by the default policy; it can
  stay empty depending on the policy.
- `Environments`: if set, the notification fires only for these environments.
- `Policy`: recipient routing strategy:
    - **No Filters** (default): forward to the distribution list.
    - **Direct subscriptions**: forward to the active subscriptions (used by
      this walkthrough).
    - **API filters**: filter recipients by rules provided in the trigger options.
    - **Dynamic**: filter users using stored rules.
- `Extra context`: JSON merged into the rendering context on top of what the
  sender provides.
- `Active`: whether the notification is active (default off — must be enabled).
- `Payload filter`: rule evaluated against the trigger payload; when it does
  not match, the notification is not sent.
- `Recipients filter`: JSON rules for dynamic recipient selection (used by the
  *Dynamic* policy).

For this walkthrough set **Policy** to *Direct subscriptions* and check
**Active**.

See [Notifications](notification.md) and
[Notification Policies](notification_policies.md) for more details.

## 6. Create the Message Template

A **Message** is the content the recipients see, rendered for one specific
Channel.

From the notification page click `Messages`{ .bc-tool-button .link } and then
`Create`{ .bc-button }. The Create form contains a `Name` field and a
`Channel` selector for the channels enabled on the event:

- `Name`: name of the template.
- `Channel`: the channel this template applies to (the channel from step 2,
  which must be enabled on the event).
- `Event` / `Notification`: pre-filled from the current context.
- `Subject`: message subject; supports template variables.
- `Content`: message body; supports template variables.
- `HTML Content`: HTML variant of the body.
- `Debug allowed`: allow debug information to be included in rendered messages.

Example content:

```
Hello { { user.first_name } }, event { { event.name } } was triggered
```

Templates are rendered per recipient with the trigger `context` plus the
event, user, assignment and channel information. See
[Create Messages](message.md) for more details.

## 7. Add the Address and Assignment

An <glossary:Address> is a delivery endpoint of a user; an
<glossary:Assignment> is the pairing "this address receives messages via this
channel".

### Address

From the sidebar open **Addresses** and click `Add`{ .bc-tool-button .action }:

- `User`: the recipient user the address belongs to.
- `Name`: label or mnemonic for the address (e.g. "work email").
- `Type`: GENERIC / EMAIL / PHONE / ACCOUNT.
- `Value`: the actual address value (e.g. `john@example.com`).

### Assignment

From the sidebar open **Assignments** and click `Add`{ .bc-tool-button .action }:

- `Address`: the address to use (the one just created).
- `Channel`: the channel paired with the address (the channel from step 2).
- `Validated`: whether the assignment has been validated.
- `Active`: whether the assignment is active.

See [Manage Addresses](address.md) for more details.

## 8. Subscribe the Recipient

A **Subscription** lets a user listen to a Notification directly, without
being part of any distribution list.

From the sidebar open **Subscriptions** and click `Add`{ .bc-tool-button .action }:

- `Notification`: the notification to listen to (step 5).
- `Assignment`: the assignment used to receive the notification (step 7).
- `Active`: whether the subscription is active.

The subscription is honoured because the notification uses the *Direct
subscriptions* policy. Alternatively it can be created through the
[Subscriptions API](../api/subscriptions.md), which requires the
`MANAGE_APPLICATION_USERS` grant.

## 9. Create the API Key

To allow a remote system to trigger the event you must create an
<glossary:API Key>.

From the sidebar open **API Keys** and click `Add`{ .bc-tool-button .action }:

- `Name`: name of the key.
- `User`: user responsible for the key.
- `Token`: auto-generated key — **displayed only once**, copy it immediately
  after saving.
- `Grants`: permissions of the key. For this walkthrough you need:
    - **Event Trigger**: allows triggering events (required for the test step).
    - **Manage Application Users**: allows managing subscriptions via the API.
    - Warning: **Full Access** grants every permission.
- `Environments`: if set, the key is only valid for these environments.

The API Key form contains the fields above. After saving, the `Token` field
shows the generated key once — copy it before leaving the page.

!!! danger "Warning"

    The key is displayed only this time. It is not possible to read it again.

See [Create API Key](api_key.md) for more details.

## 10. Trigger a Test Event

Trigger the event with the key created in step 9:

```bash
curl -X POST '[SERVER_ADDRESS]/api/o/<org>/p/<prj>/a/<app>/e/<evt>/trigger/' \
  -H 'Authorization: Key <TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{"context": {"variable1": "value1"}}'
```

Expected result: `201 CREATED` with the id of the created
<glossary:Occurrence>.

Verify the flow in the web interface:

1. From the sidebar open **Occurrences**: the new occurrence shows status
   `PROCESSED` and recipients count 1.
2. Open the occurrence: the `View deliveries (1)`{ .bc-tool-button .link }
   link opens its Deliveries.
3. The <glossary:Delivery> row shows status `DELIVERED`.

!!! hint

    Sending is asynchronous: it is handled by the background worker, so a
    freshly triggered occurrence may briefly show `PENDING`.

    If you use the `Set Address` link in the header, the `[SERVER_ADDRESS]`
    placeholder in the code examples above is replaced with your server
    address for a better experience. **No data are sent outside your browser.**

See [Trigger an Event](trigger.md) for the full API reference.
