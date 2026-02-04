# Projects API

The Projects API allows you to retrieve information about projects within an organization.

## List Projects

This endpoint retrieves a list of all projects within a specific organization.

- **Endpoint:** `GET /api/o/{org}/p/`
- **Authentication:** `ApiKeyAuthentication`
- **Permissions:** `organization:read`

### URL Parameters

-   `org` (string, required): The slug of the organization.

### Response

-   **`200 OK`**: The request was successful. The response body will contain a list of project objects.
    ```json
    [
        {
            "name": "<project_name>",
            "slug": "<project_slug>",
            "applications": "<url_to_applications_list>",
            "channels": "<url_to_channels_list>",
            "distribution_lists": "<url_to_distribution_lists_list>"
        },
        ...
    ]
    ```
-   **`401 UNAUTHORIZED`**: The API key is invalid or missing.
-   **`403 FORBIDDEN`**: The API key does not have the required `organization:read` permission.
-   **`404 NOT FOUND`**: The specified organization does not exist.

---

## Retrieve a Project

This endpoint retrieves the details of a specific project.

- **Endpoint:** `GET /api/o/{org}/p/{prj}/`
- **Authentication:** `ApiKeyAuthentication`
- **Permissions:** `organization:read`

### URL Parameters

-   `org` (string, required): The slug of the organization.
-   `prj` (string, required): The slug of the project to retrieve.

### Response

-   **`200 OK`**: The request was successful. The response body will contain the project details.
    ```json
    {
        "name": "<project_name>",
        "slug": "<project_slug>",
        "applications": "<url_to_applications_list>",
        "channels": "<url_to_channels_list>",
        "distribution_lists": "<url_to_distribution_lists_list>"
    }
    ```
-   **`401 UNAUTHORIZED`**: The API key is invalid or missing.
-   **`403 FORBIDDEN`**: The API key does not have the required `organization:read` permission.
-   **`404 NOT FOUND`**: The specified organization or project does not exist.
