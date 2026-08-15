# User Management and Integration

A **User** is a person that can log into Bitcaster and/or receive
notifications. Users are global to the installation: being member of an
organization (see [Manage Members](member.md)) gives them a role there and
lets them hold the <glossary:Address>es — email, phone, ... — through which
they can be reached by notifications.

Managing users in Bitcaster can be done manually, via bulk imports, or through continuous integration with external systems (like HRIS, CRM, or Custom Apps) using the API.

---

## 1. Bulk Import (CSV)

The fastest way to onboard many users is using a CSV file. Bitcaster automatically maps common fields and supports custom metadata.

### CSV Structure
Create a CSV file with the following headers:
- **Required**: `email`
- **Optional**: `first_name`, `last_name`
- **Metadata**: Any column starting with `custom__` will be added to the user's metadata (e.g., `custom__office`, `custom__department`).

**Example CSV**:
```csv
email,first_name,last_name,custom__office,custom__department
mario.rossi@example.com,Mario,Rossi,Milan,IT
anna.verdi@example.com,Anna,Verdi,Rome,Sales
```

### Import Process
1. Navigate to the **Users** section in your Organization.
2. Select **Import Members** (if available in your console).
3. Upload the CSV. Bitcaster will:
    - Create new users if they don't exist.
    - Enroll existing users into the current Organization.
    - Create a default "Email" address for each user.

---

## 2. Bulk Import via CLI (bc)

For administrators with server access, Bitcaster provides a command-line tool to perform mass imports. This is faster for very large datasets as it avoids web timeouts.

### Command: `bc import users`

**Basic Usage**:
```bash
bc import users path/to/file.csv
```

**Options**:
- `--org SLUG`: Specify the organization slug. If omitted, Bitcaster will automatically select the **first available organization** that is not "os4d".
- `--group NAME`: Optional. Add all imported users to a specific group within the organization.

**Example**:
```bash
bc import users employees.csv --org my-company --group developers
```

---

## 3. Bulk Import via API

While Bitcaster does not have a single "bulk" endpoint, its API is optimized for high-concurrency. You can import thousands of users by sending multiple requests in parallel. Since the endpoint is **idempotent**, it's safe to retry if a request fails.

### Recommended Strategy: Parallel Workers
Instead of a slow serial loop, use a script with a pool of workers.

**Example Python Script (using `httpx` for high performance)**:
```python
import asyncio
import httpx

API_URL = "https://bitcaster.yourdomain.com/api/v1/user/my-org/"
HEADERS = {"Authorization": "Key YOUR_API_KEY"}

async def create_user(client, user_data):
    response = await client.post(API_URL, json=user_data)
    print(f"User {user_data['email']}: {response.status_code}")

async def bulk_import(user_list):
    async with httpx.AsyncClient(headers=HEADERS) as client:
        tasks = [create_user(client, user) for user in user_list]
        await asyncio.gather(*tasks)

# List of users to import
users = [
    {"email": "user1@example.com", "first_name": "User", "last_name": "One"},
    {"email": "user2@example.com", "first_name": "User", "last_name": "Two"},
    # ... more users
]

asyncio.run(bulk_import(users))
```

### Advantages of this approach:
- **Scalability**: You can process hundreds of users per second.
- **Granular Error Handling**: If one user fails (e.g., invalid email), the others are still processed.
- **Real-time Feedback**: You get an immediate `201 Created` or `200 OK` for every single record.

---

## 3. API Integration and Syncing

To keep Bitcaster users in sync with an external source of truth, use the User API. The API is designed to be **idempotent**, meaning you can call it multiple times without creating duplicates.

### Endpoint: `/api/v1/user/{org_slug}/`

### Create or Enroll (Provisioning)
To ensure a user exists and is part of your organization:
```bash
curl -X POST https://bitcaster.yourdomain.com/api/v1/user/my-org/ \
     -H "Authorization: Key YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@company.com",
       "first_name": "John",
       "last_name": "Doe",
       "custom_fields": {"external_id": "12345", "role": "editor"}
     }'
```
*If the user exists, Bitcaster just ensures they are enrolled in "my-org" and linked to the default group.*

### Smart Syncing (Metadata Updates)
When updating users, Bitcaster provides a powerful `_mode` parameter to control how metadata (`custom_fields`) is updated. This prevents external systems from accidentally wiping out local data.

**Endpoint**: `PATCH /api/v1/user/{org_slug}/{username}/`

| Mode | Behavior |
| :--- | :--- |
| **merge** (Default) | Deep merge: adds/updates new keys, keeps existing ones. |
| **override** | Shallow update: replaces top-level keys. |
| **rewrite** | Total replacement: the metadata becomes exactly what you send. |
| **remove** | Deletes the keys provided in the request from the user's profile. |

**Example: Partial Sync** (Only update office, leave department alone):
```bash
curl -X PATCH https://bitcaster.yourdomain.com/api/v1/user/my-org/john.doe@company.com/ \
     -H "Authorization: Key YOUR_API_KEY" \
     -d '{
       "custom_fields": {"office": "London"},
       "_mode": "merge"
     }'
```

---

## 3. Best Practices for Integration

1. **Use Email as ID**: Bitcaster uses the email/username as the primary identifier for API calls.
2. **Store External IDs**: Always store your source system's ID in `custom_fields.external_id`. This makes it easier to reference the user in future sync tasks.
3. **Automate Addresses**: If you use SMS or Slack, remember to also sync the user's specific addresses via the `/address/` sub-endpoint after creating the user.
