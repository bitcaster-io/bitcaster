---
tags:
   - Monitor

---
# Configure Monitors

Monitors allow you to "trigger" an application event based on an external event.

Each monitor must use an <glossary:Agent> to check for changes.

## How to add a Monitor:

1. Go to <https://SERVER_ADDRESS/admin/bitcaster/monitor/> and click
   `Add Monitor`{class='bc-tool-button' }. The list page shows the existing
   monitors with `Name`, `Event`, `Agent` and `Active` columns and a search box.

1. Provide a name, select your event and the Agent and click `Save`{class='bc-button' }.
   The form contains a `Name` field, an `Event` selector, an `Agent` selector
   and the `Active` checkbox.

1. Configure your Agent: open the monitor and click the `Configure` button.
   The configuration form shows the fields specific to the chosen agent (e.g.
   IMAP server and credentials for the *AgentImap* agent, folders and patterns
   for the filesystem agents). Save the configuration.

1. Configure Agent scheduling: the monitor checks for changes on a schedule
   expressed in crontab syntax, e.g. `*/5 * * * *` to run every five minutes.

1. Review your settings: the monitor's detail page shows the `Name`, `Event`,
   `Agent`, `Active` state and the `Configuration` applied. Use the `Test`
   button to run the agent once and verify that the configured detection
   works.
