# Register Application Events

An **Event** is the entry point of Bitcaster: anything that happens in your
systems — a payment completed, a user registered, an alert raised — can become
an Event. When an Event is triggered, Bitcaster matches it against its
active <glossary:Notification>s and delivers the messages to the recipients.
Declaring the Events of your application is what makes those happenings
reachable by the API.

To allow Bitcaster to process [events][event], those need to be listed and configured.

## Create Event

The Event form contains:

- `Name`: name of the event (also used to build its trigger).
- `Description`: description of the event.
- `Active`: enable/disable notifications for this event.
- `Newsletter mode`: do not customise notifications per single user.
- `Channels`: the channels this event may use; recipients on other channels
  are ignored.
- `Occurrence retention`: how many days occurrences are kept before being
  purged (if empty the system default is used).

After the Event has been successfully created, you can choose which <glossary:Channel>s
you want make available for this

## Enable Channels

Setup which channels can be used to notify this event: open the event's detail
page, tick the channels in the `Channels` selector and save.

## Event Simulations

Event Simulations let you dry-run an event before it goes live: Bitcaster
collects the recipients and renders the messages **without sending anything**.

1. Open the event and click **Run simulation**
1. Provide the **context** (the payload that would be sent by the caller) and
   optionally the routing **options**
1. Choose the **mode**:
   - **fast** — collect recipients only, no rendering
   - **partial** — collect recipients and render up to the configured limit
   - **full** — collect recipients and render for all of them
1. Save

The simulation status moves from `NEW` to `PROCESSED` when it completes. From
the **Delivery Simulations** page you can inspect every simulated delivery:
the recipient, the notification, the message template used and the rendered
content (`subject`/`message`/`html_message`). Deliveries whose channel has no
matching <glossary:Message> are flagged as **missing template**.

Simulations are kept for the configured retention
(`EVENT_SIMULATION_RETENTION`) and purged automatically.
