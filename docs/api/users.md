# Users API

The Users API allows you to manage users and their addresses within an organization.

## List Users

This endpoint retrieves a list of all users within a specific organization.

- **Endpoint:** `GET /api/o/{org}/u/`
- **Authentication:** `ApiKeyAuthentication`
- **Permissions:** `user:read`

### URL Parameters

-   `org` (string, required): The slug of the organization.

### Response

-   **`200 OK`**: The request was successful. The response body will contain a list of user objects.
    ```json
    [
        {
            "id": 1,
            "email": "user1@example.com",
            "username": "user1",
            "first_name": "User",
            "last_name": "One",
            "locked": false
        },
        ...
    ]
    ```
-   **`401 UNAUTHORIZED`**: The API key is invalid or missing.
-   **`403 FORBIDDEN`**: The API key does not have the required `user:read` permission.
-   **`404 NOT FOUND`**: The specified organization does not exist.

---

## Create a User

This endpoint creates a new user within a specific organization.

- **Endpoint:** `POST /api/o/{org}/u/`
- **Authentication:** `ApiKeyAuthentication`
- **Permissions:** `user:write`

### URL Parameters

-   `org` (string, required): The slug of the organization.

### Request Body

-   `email` (string, required): The email address of the new user.
-   `first_name` (string, optional): The first name of the new user.
-   `last_name` (string, optional): The last name of the new user.
-   `custom_fields` (object, optional): A JSON object with custom fields.

    ```json
    {
        "email": "new.user@example.com",
        "first_name": "New",
        "last_name": "User"
    }
    ```

### Response

-   **`201 CREATED`**: The user was created successfully. The response body will contain the details of the new user.
    ```json
    {
        "id": 2,
        "email": "new.user@example.com",
        "username": "new.user@example.com",
        "first_name": "New",
        "last_name": "User",
        "custom_fields": {}
    }
    ```
-   **`400 BAD REQUEST`**: The request was invalid (e.g., the user already exists).
-   **`401 UNAUTHORIZED`**: The API key is invalid or missing.
-   **`403 FORBIDDEN`**: The API key does not have the required `user:write` permission.
-   **`404 NOT FOUND`**: The specified organization does not exist.

---

## Retrieve a User

This endpoint retrieves the details of a specific user.

- **Endpoint:** `GET /api/o/{org}/u/{username}/`
- **Authentication:** `ApiKeyAuthentication`
- **Permissions:** `user:read`

### URL Parameters

-   `org` (string, required): The slug of the organization.
-   `username` (string, required): The username of the user to retrieve.

### Response

-   **`200 OK`**: The request was successful. The response body will contain the user details.
    ```json
    {
        "id": 1,
        "email": "user1@example.com",
        "username": "user1",
        "first_name": "User",
        "last_name": "One",
        "locked": false
    }
    ```
-   **`401 UNAUTHORIZED`**: The API key is invalid or missing.
-   **`403 FORBIDDEN`**: The API key does not have the required `user:read` permission.
-   **`404 NOT FOUND`**: The specified organization or user does not exist.

---

## Update a User

This endpoint updates the details of a specific user.

- **Endpoint:** `PUT /api/o/{org}/u/{username}/` or `PATCH /api/o/{org}/u/{username}/`
- **Authentication:** `ApiKeyAuthentication`
- **Permissions:** `user:write`

### URL Parameters

-   `org` (string, required): The slug of the organization.
-   `username` (string, required): The username of the user to update.

### Request Body

-   `first_name` (string, optional): The users first name.
-   `last_name` (string, optional): The users last name.
-   `locked` (boolean, optional): Whether the user is locked or not.
-   `custom_fields` (object, optional): A JSON object with custom fields.
-   `_mode` (string, optional): The update mode for the `custom_fields`. Can be `REPLACE`, `MERGE`, or `IGNORE`. Defaults to `IGNORE`.

    ```json
    {
        "first_name": "Updated",
        "custom_fields": {
            "new_field": "new_value"
        },
        "_mode": "MERGE"
    }
    ```

### Response

-   **`200 OK`**: The user was updated successfully.
-   **`400 BAD REQUEST`**: The request was invalid.
-   **`401 UNAUTHORIZED`**: The API key is invalid or missing.
-   **`403 FORBIDDEN`**: The API key does not have the required `user:write` permission.
-   **`404 NOT FOUND`**: The specified organization or user does not exist.

---

## List User Addresses

This endpoint retrieves a list of all addresses for a specific user.

- **Endpoint:** `GET /api/o/{org}/u/{username}/address/`
- **Authentication:** `ApiKeyAuthentication`
- **Permissions:** `user:read`

### URL Parameters

-   `org` (string, required): The slug of the organization.
-   `username` (string, required): The username of the user.

### Response

-   **`200 OK`**: The request was successful. The response body will contain a list of address objects.
    ```json
    [
        {
            "name": "email",
            "value": "user1@example.com"
        },
        ...
    ]
    ```
-   **`401 UNAUTHORIZED`**: The API key is invalid or missing.
-   **`403 FORBIDDEN`**: The API key does not have the required `user:read` permission.
-   **`404 NOT FOUND`**: The specified organization or user does not exist.

---

## Add an Address to a User

This endpoint adds a new address to a specific user.

- **Endpoint:** `POST /api/o/{org}/u/{username}/address/`
- **Authentication:** `ApiKeyAuthentication`
- **Permissions:** `user:write`

### URL Parameters

-   `org` (string, required): The slug of the organization.
-   `username` (string, required): The username of the user.

### Request Body

-   `name` (string, required): The name of the address (e.g., "email", "phone").
-   `value` (string, required): The value of the address.

    ```json
    {
        "name": "phone",
        "value": "+1234567890"
    }
    ```

### Response

-   **`200 OK`**: The address was added successfully.
-   **`400 BAD REQUEST`**: The request was invalid.
-   **`401 UNAUTHORIZED`**: The API key is invalid or missing.
-   **`403 FORBIDDEN`**: The API key does not have the required `user:write` permission.
-   **`404 NOT FOUND`**: The specified organization or user does not exist.
