# Organizations API

The Organizations API allows you to retrieve information about organizations.

## Retrieve an Organization

This endpoint retrieves the details of a specific organization.

- **Endpoint:** `GET /api/o/{org}/`
- **Authentication:** `ApiKeyAuthentication`
- **Permissions:** `organization:read`

### URL Parameters

-   `org` (string, required): The slug of the organization to retrieve.

### Response

-   **`200 OK`**: The request was successful. The response body will contain the organization details.
    ```json
    {
        "name": "<organization_name>",
        "slug": "<organization_slug>",
        "users": "<url_to_users_list>",
        "projects": "<url_to_projects_list>",
        "channels": "<url_to_channels_list>"
    }
    ```
-   **`401 UNAUTHORIZED`**: The API key is invalid or missing.
-   **`403 FORBIDDEN`**: The API key does not have the required `organization:read` permission.
-   **`404 NOT FOUND`**: The specified organization does not exist.
