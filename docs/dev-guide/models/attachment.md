# Attachment

An `Attachment` is a file owned by an `Application` that can be attached to notifications.

## Purpose

The `Attachment` stores a file uploaded to the `attachments/` upload location together with metadata (filename, MIME type, size) and a unique `correlation_id` used to reference the attachment externally. Records are created when an application uploads a file for use with a notification. On save the model refreshes `size` from the document's file size and generates a `correlation_id` from a UUID hex if one is not already set. `natural_key` is (`correlation_id`, *`Application.natural_key()`).

## Connections

- `application` -> `Application` (on_delete=CASCADE, related_name="attachments")
- `correlation_id` is `unique=True`

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| application | ForeignKey -> Application | No | - | Application owner of this Attachment |
| correlation_id | SlugField | No | uuid4 | Unique human readable identifier for the attachment |
| filename | CharField(256) | Yes | None | Filename to use when downloading the attachment |
| document | FileField(upload_to="attachments/") | No | - | Attachment file |
| mime_type | CharField(256) | No | - | MIME type of the file. It will be auto-detected if not provided |
| size | PositiveIntegerField | No | 0 | Attachment size in bytes |
| version | IntegerVersionField | No | - | Version number of the record |
| last_updated | DateTimeField | No | - | Record last update time (auto_now) |
| created | DateTimeField | No | - | Record creation time (auto_now_add) |
