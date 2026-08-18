# Dispatchers

A **Dispatcher** is the provider-specific component that physically delivers a
message to its destination: email via SMTP, Slack via webhook, SMS via Twilio,
and so on.

The available dispatchers are:

- [Brevo](brevo.md)
- [Email](email.md)
- [Gmail](gmail.md)
- [Log](log.md)
- [Mailgun](mailgun.md)
- [Mailjet](mailjet.md)
- [Postmark](postmark.md)
- [RabbitMQ](rabbitmq.md)
- [Resend](resend.md)
- [SES](ses.md)
- [SendGrid](sendgrid.md)
- [Slack](slack.md)
- [Sys](sys.md)
- [Teams](teams.md)
- [Twilio](twilio.md)
- [User Message](user_message.md)
- [X](x.md)

See [Development Guide: Dispatchers](../../dev-guide/dispatchers.md) for
details on how to implement a new dispatcher.
