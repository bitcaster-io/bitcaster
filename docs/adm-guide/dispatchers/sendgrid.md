# SendGrid Dispatcher

The SendGrid dispatcher sends notifications via SendGrid's API.

## Configuration

The following parameters are available to configure the SendGrid dispatcher:

- **API Key** (required): Your SendGrid API Key.
- **Sender Domain** (optional): The domain verified in SendGrid for sending.
- **From Address** (optional): Override the sender email address.
- **From Name** (optional): Override the sender display name.

## How to use

1.  Select `SendGrid` as dispatcher for a Channel
2.  Fill the form with your SendGrid API Key and optionally a from address/name.
3.  Save the Channel.

Now you can add this channel to your Application and send notifications.
