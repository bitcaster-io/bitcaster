# Subscriptions API

The Subscriptions API allows a user to directly subscribe to a Notification, without being a member of any Distribution List. The user is derived from the subscribed Assignment's address.

## Subscribe

This endpoint creates (or updates) a subscription for the given assignment to the given notification.

- **Endpoint:** `POST /api/o/{org}/p/{prj}/a/{app}/n/{notification_pk}/subscribe/`
- **Authentication:** `ApiKeyAuthentication`
- **Permissions:** `MANAGE_APPLICATION_USERS` grant on the application

### URL Parameters

-   `org` (string, required): The slug of the organization.
-   `prj` (string, required): The slug of the project.
-   `app` (string, required): The slug of the application.
-   `notification_pk` (integer, required): The id of the notification to subscribe to.

### Request Body

-   `assignment` (integer, required): The id of the assignment used to receive the notification.
-   `active` (boolean, optional): Status of the subscription. Defaults to `true` if not provided.

```json
{
    "assignment": 33,
    "active": true
}
```

### Response

-   **`201 CREATED`**: The subscription was created. The response body contains the subscription id.
    ```json
    {
        "subscription": 100
    }
    ```
-   **`200 OK`**: The subscription already existed; the payload's `active` value has been applied to it. The request is idempotent.
    ```json
    {
        "subscription": 100
    }
    ```
-   **`400 BAD REQUEST`**: The request was invalid (e.g., missing `assignment`).
-   **`403 FORBIDDEN`**: The API key does not have the required `MANAGE_APPLICATION_USERS` grant or does not match the application scope.
-   **`404 NOT FOUND`**: The notification or the assignment does not exist.

---

## Unsubscribe

This endpoint deactivates the subscription of the given assignment to the given notification.

- **Endpoint:** `DELETE /api/o/{org}/p/{prj}/a/{app}/n/{notification_pk}/subscribe/`
- **Authentication:** `ApiKeyAuthentication`
- **Permissions:** `MANAGE_APPLICATION_USERS` grant on the application

### URL Parameters

Same as [Subscribe](#subscribe).

### Request Body

-   `assignment` (integer, required): The id of the assignment to unsubscribe.

```json
{
    "assignment": 33
}
```

### Response

-   **`200 OK`**: The subscription has been deactivated (`active = false`). The request is idempotent.
    ```json
    {
        "subscription": 100
    }
    ```
-   **`403 FORBIDDEN`**: The API key does not have the required `MANAGE_APPLICATION_USERS` grant or does not match the application scope.
-   **`404 NOT FOUND`**: The notification or the subscription does not exist.
