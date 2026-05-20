# User Messages Dispatcher

The User Messages dispatcher sends notifications as in-app messages visible in the user's Bitcaster console.

## Configuration

The following parameters are required to configure the User Messages dispatcher:

- **Auto Assign**: Automatically assign users to this channel when they receive a message.
- **Event**: The event to trigger when notifying users of new messages.
- **Message TTL**: Number of days read messages are kept before automatic deletion.

## How to use

1.  Select `User Messages` as dispatcher for a Channel
2.  Configure the associated event, auto-assign behavior, and message retention.
3.  Save the Channel.

Now you can add this channel to your Application and send notifications. Users will see messages in their Bitcaster console under the messages section.
