# Trigger an Event

You can trigger an event by sending a `POST` request to its trigger URL. This will create a new <glossary:Occurrence> and start the process of sending notifications to the subscribers of the event.

**Endpoint:** `POST /api/o/{org}/p/{proj}/a/{app}/e/{event}/trigger/`

## Authentication

Authentication is performed via an <glossary:API Key> sent in the `Authorization` header.

`Authorization: Key <YOUR_API_KEY>`

The API Key must have the `event:trigger` grant for the specified event's application.

### Web Credentials

Triggers coming from a browser must use a **Web API Key** or a **Client Token** instead. Web credentials require the request to carry an `Origin` header matching one of the configured allowed origins, and:

-   they can only have the `web:trigger` grant;
-   they cannot auto-create events or use `filters`;
-   the serialized `context` payload is limited to `TRIGGER_CONTEXT_MAX_SIZE` bytes (default `32768`).

See [Trigger Events from a Web Page](web-client.md) for the recommended setup.

## Request Body

The request body should be a JSON object with the following properties:

-   **`context`** (optional): A dictionary of key-value pairs that will be available in the message templates.
-   **`options`** (optional): A dictionary of options to customize the notification process.

### `options` object

The `options` object can contain the following keys:

-   `limit_to`: A list of recipient addresses to limit the notifications to.
-   `channels`: A list of channel names to limit the notifications to.
-   `environs`: A list of environment names to limit the notifications to.
-   `filters`: A set of rules to dynamically filter recipients.

#### The `filters` object

The `filters` object allows for dynamic filtering of recipients based on user attributes. It is only considered for notifications that have the `external_filtering` flag enabled.

Like fixed rules, the `filters` object supports **Context Variables**. You can use `{ { ... } }` placeholders that will be rendered using the `context` provided in the same request.

**Example with Context Variables:**

```json
{
    "context": {
        "target_region": "emea"
    },
    "options": {
        "filters": {
            "include": {
                "custom_fields__region": "{{ target_region }}"
            }
        }
    }
}
```

The object has two main keys:
- `include`: A list of rules to select users.
- `exclude`: A list of rules to filter out users from the selection.

The structure of the rules follows the logic described in the [filtering documentation](../dev-guide/filtering.md).

**Example:**

```json
{
    "context": {
        "transaction_id": "12345",
        "amount": "100.00"
    },
    "options": {
        "channels": ["email", "sms"],
        "filters": {
            "include": [
                {"is_staff": true},
                {"groups__name": "support"}
            ],
            "exclude": {
                "last_login__isnull": true
            }
        }
    }
}
```

In this example, the notification will be sent to all staff members who are also in the "support" group, excluding those who have never logged in. The notification will only be sent through the "email" and "sms" channels.

## Response

-   **`201 CREATED`**: The event was triggered successfully. The response body will contain the ID of the created occurrence.
    ```json
    {
        "occurrence": "<occurrence_id>"
    }
    ```
-   **`400 BAD REQUEST`**: The request was invalid. The response body will contain details about the error.
-   **`401 UNAUTHORIZED`**: The API key is invalid, revoked, or expired.
-   **`403 FORBIDDEN`**: The API key does not have the required permissions, or the `Origin` header is missing or not allowed.
-   **`404 NOT FOUND`**: The organization, project, application, or event does not exist.
