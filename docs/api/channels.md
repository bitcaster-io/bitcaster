# Channels API

The Channels API allows you to retrieve information about channels within an organization or a project.

## List Organization Channels

This endpoint retrieves a list of all channels within a specific organization.

- **Endpoint:** `GET /api/o/{org}/c/`
- **Authentication:** `ApiKeyAuthentication`
- **Permissions:** `organization:read`

### URL Parameters

-   `org` (string, required): The slug of the organization.

### Response

-   **`200 OK`**: The request was successful. The response body will contain a list of channel objects.
    ```json
    [
        {
            "name": "<channel_name>",
            "slug": "<channel_slug>",
            "type": "<channel_type>",
            "enabled": true
        },
        ...
    ]
    ```
-   **`401 UNAUTHORIZED`**: The API key is invalid or missing.
-   **`403 FORBIDDEN`**: The API key does not have the required `organization:read` permission.
-   **`404 NOT FOUND`**: The specified organization does not exist.

---

## List Project Channels

This endpoint retrieves a list of all channels within a specific project.

- **Endpoint:** `GET /api/o/{org}/p/{prj}/c/`
- **Authentication:** `ApiKeyAuthentication`
- **Permissions:** `organization:read`

### URL Parameters

-   `org` (string, required): The slug of the organization.
-   `prj` (string, required): The slug of the project.

### Response

-   **`200 OK`**: The request was successful. The response body will contain a list of channel objects.
    ```json
    [
        {
            "name": "<channel_name>",
            "slug": "<channel_slug>",
            "type": "<channel_type>",
            "enabled": true
        },
        ...
    ]
    ```
-   **`401 UNAUTHORIZED`**: The API key is invalid or missing.
-   **`403 FORBIDDEN`**: The API key does not have the required `organization:read` permission.
-   **`404 NOT FOUND`**: The specified organization or project does not exist.
