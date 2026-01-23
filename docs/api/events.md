# Events API

The Events API allows you to list and trigger events within an application.

## List Events

This endpoint retrieves a list of all events within a specific application.

- **Endpoint:** `GET /api/o/{org}/p/{prj}/a/{app}/e/`
- **Authentication:** `ApiKeyAuthentication`
- **Permissions:** `event:list`

### URL Parameters

-   `org` (string, required): The slug of the organization.
-   `prj` (string, required): The slug of the project.
-   `app` (string, required): The slug of the application.

### Response

-   **`200 OK`**: The request was successful. The response body will contain a list of event objects.
    ```json
    [
        {
            "name": "<event_name>",
            "slug": "<event_slug>"
        },
        ...
    ]
    ```
-   **`401 UNAUTHORIZED`**: The API key is invalid or missing.
-   **`403 FORBIDDEN`**: The API key does not have the required `event:list` permission.
-   **`404 NOT FOUND`**: The specified organization, project, or application does not exist.

---

## Trigger an Event

This endpoint triggers a specific event.

- **Endpoint:** `POST /api/o/{org}/p/{prj}/a/{app}/e/{evt}/trigger/`
- **Authentication:** `ApiKeyAuthentication`
- **Permissions:** `event:trigger`

### URL Parameters

-   `org` (string, required): The slug of the organization.
-   `prj` (string, required): The slug of the project.
-   `app` (string, required): The slug of the application.
-   `evt` (string, required): The slug of the event to trigger.

### Request Body

-   `context` (object, optional): A JSON object with context data to be used in the notification templates.
-   `options` (object, optional): A JSON object with options to customize the notification process. See the [Triggering Events documentation](../adm-guide/trigger.md) for more details.

    ```json
    {
        "context": {
            "variable1": "value1"
        },
        "options": {
            "channels": ["email"]
        }
    }
    ```

### Response

-   **`201 CREATED`**: The event was triggered successfully. The response body will contain the ID of the created occurrence.
    ```json
    {
        "occurrence": "<occurrence_id>"
    }
    ```
-   **`400 BAD REQUEST`**: The request was invalid.
-   **`401 UNAUTHORIZED`**: The API key is invalid or missing.
-   **`403 FORBIDDEN`**: The API key does not have the required `event:trigger` permission.
-   **`404 NOT FOUND`**: The specified organization, project, aplication, or event does not exist.
