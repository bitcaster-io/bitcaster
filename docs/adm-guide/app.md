# Add Application

An **Application** is the container of a single product or service in
Bitcaster: every <glossary:Event>, <glossary:Notification>, channel binding,
attachment and API key belongs to an Application. Grouping by application lets
you scope routing, monitoring and keys to one product instead of sharing them
across everything.

Now that your Organization and Project have been configured, you can start adding all the Applications
that you want to be served by Bitcaster.


Click on the `Add Application`{ .bc-tool-button .action } button on the top right of the
[Project page](https://SERVER_ADDRESS/admin/bitcaster/project/current/){:target=_bc}

or navigate to <https://SERVER_ADDRESS/admin/bitcaster/application/add/>{: target='link' }

The Application form contains:

- `Name`: name of the application (the system that will trigger the events).
- `Project`: parent project (pre-filled when created from the project page).
- `Owner`: user responsible for the application.
- `Active`: whether the application accepts triggers.
- `Auto create events`: if enabled, unknown events are automatically created
  when they are triggered.
- `Auto create event options`: options applied to auto-created events.
- `From email`: default "from" address for emails.
- `Subject prefix`: default subject prefix for messages.
- `Advanced configuration`: JSON for advanced features (e.g. attachment
  support).

Now you are ready to [configure your Application](app.md)
adding <glossary:Event>, <glossary:Notification> and <glossary:Distribution List>
