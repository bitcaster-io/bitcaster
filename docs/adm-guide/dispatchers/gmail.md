# GMail Dispatcher

The GMail dispatcher sends notifications via Google's SMTP server.

## Configuration

The following parameters are required to configure the GMail dispatcher:

- **Username**: Your GMail username (e.g., `user@gmail.com`).
- **Password**: Your GMail password. You might need to use an "App Password" if you have 2-Factor Authentication enabled on your Google account.
- **Timeout**: The connection timeout in seconds. Must be between 0 and 5.

The dispatcher will connect to `smtp.gmail.com` on port `587` and use TLS encryption.

## How to use

1.  Select `GMail` as dispatcher for a Channel
2.  Fill the form with your GMail credentials.
3.  Save the Channel.

Now you can add this channel to your Application and send notifications.
