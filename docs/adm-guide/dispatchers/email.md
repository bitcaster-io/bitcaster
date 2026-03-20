# Email Dispatcher

The Email dispatcher sends notifications via SMTP.

## Configuration

The following parameters are required to configure the Email dispatcher:

- **Host**: The SMTP server hostname or IP address.
- **Port**: The SMTP server port.
- **Username**: The username for SMTP authentication.
- **Password**: The password for SMTP authentication.
- **TLS**: Check this to enable Transport Layer Security (TLS).
- **SSL**: Check this to enable Secure Sockets Layer (SSL).
- **Timeout**: The connection timeout in seconds. Must be between 0 and 5.

## How to use

1.  Select `Email` as dispatcher for a Channel
2.  Fill the form with the connection parameters to your SMTP server
3.  Save the Channel.

Now you can add this channel to your Application and send notifications.
