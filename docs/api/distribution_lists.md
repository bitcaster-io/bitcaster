# Distribution Lists API

The Distribution Lists API allows you to manage distribution lists and their members within a project.

## List Distribution Lists

This endpoint retrieves a list of all distribution lists within a specific project.

- **Endpoint:** `GET /api/o/{org}/p/{prj}/d/`
- **Authentication:** `ApiKeyAuthentication`
- **Permissions:** `distributionlist:read`

### URL Parameters

-   `org` (string, required): The slug of the organization.
-   `prj` (string, required): The slug of the project.

### Response

-   **`200 OK`**: The request was successful. The response body will contain a list of distribution list objects.
    ```json
    [
        {
            "name": "<distribution_list_name>",
            "id": 123,
            "members": "<url_to_members_list>"
        },
        ...
    ]
    ```
-   **`401 UNAUTHORIZED`**: The API key is invalid or missing.
-   **`403 FORBIDDEN`**: The API key does not have the required `distributionlist:read` permission.
-   **`404 NOT FOUND`**: The specified organization or project does not exist.

---

## Create a Distribution List

This endpoint creates a new distribution list within a specific project.

- **Endpoint:** `POST /api/o/{org}/p/{prj}/d/`
- **Authentication:** `ApiKeyAuthentication`
- **Permissions:** `distributionlist:write`

### URL Parameters

-   `org` (string, required): The slug of the organization.
-   `prj` (string, required): The slug of the project.

### Request Body

-   `name` (string, required): The name of the new distribution list.

    ```json
    {
        "name": "My New Distribution List"
    }
    ```

### Response

-   **`201 CREATED`**: The distribution list was created successfully. The response body will contain the details of the new distribution list.
    ```json
    {
        "name": "My New Distribution List",
        "id": 124,
        "members": "<url_to_members_list>"
    }
    ```
-   **`400 BAD REQUEST`**: The request was invalid (e.g., the name already exists).
-   **`401 UNAUTHORIZED`**: The API key is invalid or missing.
-   **`403 FORBIDDEN`**: The API key does not have the required `distributionlist:write` permission.
-   **`404 NOT FOUND`**: The specified organization or project does not exist.

---

## Retrieve a Distribution List

This endpoint retrieves the details of a specific distribution list.

- **Endpoint:** `GET /api/o/{org}/p/{prj}/d/{pk}/`
- **Authentication:** `ApiKeyAuthentication`
- **Permissions:** `distributionlist:read`

### URL Parameters

-   `org` (string, required): The slug of the organization.
-   `prj` (string, required): The slug of the project.
-   `pk` (integer, required): The ID of the distribution list to retrieve.

### Response

-   **`200 OK`**: The request was successful. The response body will contain the distribution list details.
    ```json
    {
        "name": "<distribution_list_name>",
        "id": 123,
        "members": "<url_to_members_list>"
    }
    ```
-   **`401 UNAUTHORIZED`**: The API key is invalid or missing.
-   **`403 FORBIDDEN`**: The API key does not have the required `distributionlist:read` permission.
-   **`404 NOT FOUND`**: The specified organization, project, or distribution list does not exist.

---

## Add Recipients to a Distribution List

This endpoint adds one or more recipients to a specific distribution list.

- **Endpoint:** `POST /api/o/{org}/p/{prj}/d/{pk}/add/`
- **Authentication:** `ApiKeyAuthentication`
- **Permissions:** `distributionlist:write`

### URL Parameters

-   `org` (string, required): The slug of the organization.
-   `prj` (string, required): The slug of the project.
-   `pk` (integer, required): The ID of the distribution list.

### Request Body

A JSON array of email addresses to add to the distribution list.

```json
[
    "user1@example.com",
    "user2@example.com"
]
```

### Response

-   **`200 OK`**: The recipients were added successfully.
-   **`400 BAD REQUEST`**: The request was invalid (e.g., invalid email addresses).
-   **`401 UNAUTHORIZED`**: The API key is invalid or missing.
-   **`403 FORBIDDEN`**: The API key does not have the required `distributionlist:write` permission.
-   **`404 NOT FOUND`**: The specified organization, project, or distribution list does not exist.

---

## List Distribution List Members

This endpoint retrieves a list of all members of a specific distribution list.

- **Endpoint:** `GET /api/o/{org}/p/{prj}/d/{pk}/m/`
- **Authentication:** `ApiKeyAuthentication`
- **Permissions:** `distributionlist:read`

### URL Parameters

-   `org` (string, required): The slug of the organization.
-   `prj` (string, required): The slug of the project.
-   `pk` (integer, required): The ID of the distribution list.

### Response

-   **`200 OK`**: The request was successful. The response body will contain a list of member objects.
    ```json
    [
        {
            "id": 1,
            "address": "user1@example.com",
            "user": "user1",
            "channel": "email",
            "active": true
        },
        ...
    ]
    ```
-   **`401 UNAUTHORIZED`**: The API key is invalid or missing.
-   **`403 FORBIDDEN`**: The API key does not have the required `distributionlist:read` permission.
-   **`404 NOT FOUND`**: The specified organization, project, or distribution list does not exist.
