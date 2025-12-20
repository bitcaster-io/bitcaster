# System API

The System API provides endpoints for monitoring the health and status of the Bitcaster instance.

## Ping

This endpoint allows you to check if the Bitcaster API is up and running and if the provided API key is valid.

- **Endpoint:** `GET /api/system/ping/`
- **Authentication:** `ApiKeyAuthentication`
- **Permissions:** `system:ping`

### Request

This endpoint does not require any request body.

### Response

- **`200 OK`**: The API is up and running. The response body will contain the name of the API key used for the request.
    ```json
    {
        "token": "<api_key_name>"
    }
    ```
- **`401 UNAUTHORIZED`**: The API key is invalid or missing.
- **`403 FORBIDDEN`**: The API key does not have the required `system:ping` permission.
