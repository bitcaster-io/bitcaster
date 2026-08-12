# Enable Project Channel

A **Project Channel** binds an abstract channel to a concrete sender for one
project: the email address the messages are sent from, the Slack workspace,
the phone number for SMS. It is what makes the project actually able to
deliver: notifications only reach recipients on channels that are enabled for
the project.


From the [Project page](https://SERVER_ADDRESS/admin/bitcaster/project/current/){:target=_bc}  click on
`Add Channel`{ .bc-tool-button .action }

The page offers two choices: **Create New Project Channel** to configure a
channel from scratch, or **Enable Abstract Channel** to reuse one of the
organization's <glossary:Abstract Channel>s.

## Create New Project Channel

Select this option and fill the form:

- `Name`: name of the channel.
- `Dispatcher`: the protocol engine used to send messages (e.g. the *Email*
  dispatcher).
- `Configuration`: dispatcher-specific settings (e.g. SMTP server and
  credentials) as JSON.
- `Protocol`: derived from the dispatcher, read-only.
- `Active`: enable/disable the channel.

Save the form; the dispatcher may ask for extra provider-specific
configuration on the following step.

## Enable Abstract Channel

If you have previously [created any Abstract Channel](abstract_channel_create.md) you can enable for the Project:

1. Select the abstract channel you want to reuse from the list.
2. Provide the concrete sender for this project (e.g. the "from" email
   address for email channels, the workspace for Slack, the phone number for
   SMS) when requested.
3. Save.

The project channel is now available in the project's Channel list and can be
attached to the project's Events.
