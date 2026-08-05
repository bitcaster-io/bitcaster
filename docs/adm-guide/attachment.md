---
tags:
   - Attachment

---
# Manage Attachments

Attachments are files that can be sent along with a notification. Each
attachment is linked to an <glossary:Application> and carries a `correlation_id`
that ties it to an <glossary:Occurrence>.

## Attachment list

The list at <https://SERVER_ADDRESS/admin/bitcaster/attachment/> shows the
application, the file name and the correlation id of every attachment.

## Upload an attachment

1. Open the [Application](app.md) the attachment belongs to
1. Upload the file through the application page or the API

The API upload endpoint
(`o/<org>/p/<prj>/a/<app>/attachment/`) accepts the file together with the
`correlation_id` of the occurrence it belongs to.

## Download

Recipients receive a signed, expiring download link
(`/attachment/download/<key>/`) in the message. The key is generated with the
`SECRET_KEY_SALT` configured in the [Configuration](../configuration.md) and expires
after the configured timeout.
