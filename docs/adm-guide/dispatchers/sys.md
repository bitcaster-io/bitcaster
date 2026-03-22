# System Email Dispatcher

The System Email dispatcher sends notifications using the email backend configured for the Bitcaster instance.
This is typically configured via environment variables.

## Configuration

This dispatcher does not require any specific configuration in the Channel settings.
It will use the email settings defined in your environment, which are the same used by Bitcaster to send system emails (e.g., password reset, user invitations).

Refer to the Bitcaster installation guide for details on how to configure the email backend.

## How to use

1.  Select `System Email` as dispatcher for a Channel
2.  Save the Channel.

Now you can add this channel to your Application and send notifications.
