# X (Twitter) Dispatcher

The X dispatcher posts notifications as tweets to the configured X account via the X API v2.

## Prerequisites

1. An X Developer account at [developer.x.com](https://developer.x.com)
2. A Project with an App configured with **OAuth 1.0a** and the Access Token set to **Read and Write** permissions

## Configuration

The following parameters are required to configure the X dispatcher. They are found in your X App's **Keys & Tokens** page under **OAuth 1.0 Keys**:

| Field | Where to find it |
|---|---|
| **Consumer Key** | Visible directly in the OAuth 1.0 Keys section. |
| **Consumer Key Secret** | Click **Show** next to the Consumer Key. |
| **Access Token** | Visible directly in the OAuth 1.0 Keys section. |
| **Access Token Secret** | Click **Show** next to the Access Token. |

## How to use

1. Open your X App at [developer.x.com](https://developer.x.com) and go to the **Keys & Tokens** page.
2. Under **OAuth 1.0 Keys**, copy the **Consumer Key** and click **Show** to copy the **Consumer Key Secret**.
3. Copy the **Access Token** and click **Show** to copy the **Access Token Secret**.
4. Ensure the token has **Read and Write** permissions under **User authentication settings**.
5. In Bitcaster, select `X (Twitter)` as the dispatcher for a Channel.
6. Click the **Configure** button on the Channel admin page.
7. Fill in all four fields: Consumer Key, Consumer Key Secret, Access Token, Access Token Secret.
8. Save the Channel configuration.

!!! note
    Messages are truncated to 280 characters to comply with X post limits.
