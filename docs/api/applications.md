# Applications API

The Applications API allows you to retrieve information about applications within a project.

## List Applications

This endpoint retrieves a list of all applications within a specific project.

- **Endpoint:** `GET /api/o/{org}/p/{prj}/a/`
- **Authentication:** `ApiKeyAuthentication`
- **Permissions:** `organization:read`

### URL Parameters

-   `org` (string, required): The slug of the organization.
-   `prj` (string, required): The slug of the project.

### Response

-   **`200 OK`**: The request was successful. The response body will contain a list of application objects.
    ```json
    [
        {
            "name": "<application_name>",
            "slug": "<application_slug>",
            "events": "<url_to_events_list>"
        },
        ...
    ]
    ```
-   **`401 UNAUTHORIZED`**: The API key is invalid or missing.
-   **`403 FORBIDDEN`**: The API key does not have the required `organization:read` permission.
-   **`404 NOT FOUND`**: The specified organization or project does not exist.
