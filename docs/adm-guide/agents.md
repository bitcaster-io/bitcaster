---
tags:
   - Agent
---
# Agent


Bitcaster implements the following Agents:

### AgentFileSystem

Detect changes in local filesystem


### AgentFTP

Detect changes in remote FTP folder


### AgentImap

Monitor IMAP mailbox and extract fields from emails matching configurable patterns.

**Configuration options:**

- **IMAP Server**: Hostname of the IMAP server
- **Port**: IMAP port (default: 993 for SSL)
- **Username**: IMAP account username
- **Password**: IMAP account password
- **Use SSL**: Enable/disable SSL connection (default: True)
- **Folder**: Mailbox folder to monitor (default: INBOX)
- **Subject pattern**: Regex with named groups to extract fields from email subject
  Example: `Alert: (?P<alert_type>\w+) - (?P<severity>\w+)`
- **Body pattern** (optional): Regex with named groups to extract fields from email body
  Example: `Error: (?P<error_msg>.+)`

**How it works:**

1. Connects to the IMAP server using configured credentials
2. Searches for unread emails in the specified folder
3. For each unread email, checks if the subject matches the configured pattern
4. If matched, extracts fields using named groups from both subject and body (if body pattern is configured)
5. Triggers the associated event with extracted fields as context
6. Tracks processed email IDs to avoid duplicate processing

**Example:**
If subject pattern is `Alert: (?P<type>\w+) - (?P<level>\w+)` and an email arrives with subject "Alert: Critical - High", the event will be triggered with context: `{"type": "Critical", "level": "High", "subject": "Alert: Critical - High", "from": "...", "date": "..."}`
