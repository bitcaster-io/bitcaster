# Create Messages

A **Message** is the content the recipients see: the subject and the body
(plain text and HTML) of a notification, rendered for one specific
<glossary:Channel>. Each channel enabled for the event needs its own message,
so an email message can be worded differently from a Slack one. The rendered
content is snapshotted when a delivery is created, so editing a message later
never changes messages that are already queued.

Select the notification you want to configure from [Notification list page](<https://SERVER_ADDRESS/admin/bitcaster/notification/>){ target=_app } and click on `messages`{ .bc-tool-button .link }

The Messages page lists the templates of the notification — `Name`, `Channel`
and `Event` columns — and shows a `Create` button.

Select one of the channels available for the Notification's event and click on `Create`{ .bc-button }

The Create form contains:

- `Name`: name of the template.
- `Channel`: the channel this template applies to.
- `Event` / `Notification`: pre-filled from the current context.
- `Subject`: message subject; supports template variables.
- `Content`: message body; supports template variables.
- `HTML Content`: HTML variant of the body.
- `Debug allowed`: allow debug information to be included in rendered messages.
