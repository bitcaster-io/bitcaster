---
tags:
   - Media

---
# Manage Media Files

Media files are the images and assets used inside your messages. They belong to
an <glossary:Application> (and optionally to a project and organization) and are
referenced from <glossary:Message> content, e.g. `[[media:logo.png]]`.

## Media list

The list at <https://SERVER_ADDRESS/admin/bitcaster/mediafile/> shows a preview
of every file with its name, size, file type and mime type. Use the filters
(organization, project, application) to scope the list.

## Upload a media file

1. Go to the media list of the application
1. Click **Add media file**
1. Select the **application** the file belongs to and pick the file
1. Save

The file is stored on the configured media storage (`STORAGE_MEDIA`) and
served through the media URL.

## Use in messages

Reference the file in a <glossary:Message> template with the `[[media:...]]`
syntax; the documentation link processor resolves it to the media URL at render
time.
