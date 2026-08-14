# Notification Policies

In Bitcaster, a **Notification Policy** determines **who** will receive a message when an event is triggered and **under what conditions**.

When an Event occurs, Bitcaster looks at all the Notifications associated with it. For each notification, it applies two levels of filtering:
1. **Payload Filter**: Should this notification be sent at all based on the data received?
2. **Recipient Policy**: Who are the specific users that should be notified?

---

## 1. Recipient Policies

The policy defines the strategy for selecting recipients. You can choose one of the following options in the Notification settings:

### No Custom Filtering (Standard)
This is the default behavior. The notification is sent to everyone subscribed to the **Distribution List** linked to the notification.
*   **Best for**: Static teams (e.g., "All System Administrators").

### Direct Subscriptions
Recipients are the **Assignments of all active Subscriptions** targeting the notification. Each user can directly subscribe to a Notification using one of their own Assignments, without being a member of any Distribution List.
*   Subscriptions are managed in the admin (inline on the **Member** page, like Assignments) or via the [Subscriptions API](../api/subscriptions.md).
*   A user can have multiple Subscriptions to the same Notification as long as the Assignments use **different channels**.
*   Like the other exclusive policies, the Distribution List, the stored `recipients_filter` and the API `options.filters` are ignored.
*   If the Assignment's channel is not in the Notification's Event channels, the assignment is excluded from processing.
*   **Best for**: Users who want to opt-in to notifications directly (e.g., "Notify me when a new release is published").

### Fixed Ruled Filtering (Dynamic)
Recipients are selected dynamically from the user database based on specific attributes.
> **Note**: This policy only selects from users who have an **active Assignment** (configured address) for the channel being used.

*   **Format**: This field must be valid **JSON**.
*   **Context Variables**: You can use template variables from the event context within the filter values. Any string value in the filter can contain Jinja2-style placeholders `{ { ... } }`

#### Using Context Variables in Filters
When an event is triggered, Bitcaster merges the provided context with the notification settings. You can use any value from this context to filter your recipients.

**Example 1: Filter by a specific username provided in the context**
If your event is triggered with context `{"target_username": "john_doe"}`, you can use:
```json
{
  "include": {
    "username": "{{ target_username }}"
  }
}
```

**Example 2: Filter by a custom attribute from the context**
If you want to notify only users in a specific department provided in the event data `{"department_id": "sales"}`:
```json
{
  "include": {
    "custom_fields__department": "{{ department_id }}"
  }
}
```

**Example 3: Complex logic with context**
You can combine multiple context variables and static values:
```json
{
  "include": {
    "is_staff": true,
    "custom_fields__office": "{{ office_name }}",
    "groups__name": "{{ required_group }}"
  }
}
```

*   **Filter Logic**:
    *   **AND**: Use a single dictionary. All keys in the dictionary must match.
    *   **OR**: Use a list of dictionaries. Any dictionary in the list matching will include the user.
    *   **Advanced**: A list of lists `[[{}, {}], [{}]]` creates `(OR group) AND (OR group)`.

#### Available Fields and Lookups
Since Bitcaster uses Django's filtering engine, you can use any field from the **User** model and its relationships using the double underscore (`__`) syntax.

| Model | Filter Path | Description |
| :--- | :--- | :--- |
| **User** | `username` | User login name |
| **User** | `email` | Primary email address |
| **User** | `first_name` | User's first name |
| **User** | `last_name` | User's last name |
| **User** | `is_staff` | Boolean: is a member of staff |
| **User** | `is_superuser` | Boolean: has all permissions |
| **User** | `is_active` | Boolean: is the account active |
| **User** | `custom_fields__<key>` | Search inside custom metadata (JSON) |
| **Group** | `groups__name` | Name of the assigned Django group |
| **Address** | `addresses__name` | Label of the address (e.g., 'Work Email') |
| **Address** | `addresses__type` | Type (EMAIL, PHONE, SMS, SLACK, etc.) |
| **Address** | `addresses__value` | The actual contact value (email, phone, etc.) |
| **Assignment** | `addresses__assignments__active` | Boolean: is the channel assignment active |
| **Assignment** | `addresses__assignments__validated` | Boolean: is the assignment verified |

#### Django Operators
You can append operators to field names for more complex matches:
*   `__contains` / `__icontains`: Partial match (case-insensitive).
*   `__startswith` / `__endswith`: Match beginning or end.
*   `__in`: Match any value in a provided list (e.g., `"pk__in": [1, 2, 3]`).
*   `__gt` / `__lt`: Greater than / Less than.

#### Security Restrictions
For security, filters containing sensitive words are **forbidden** and will trigger a validation error:
*   `password`, `token`, `secret`, `key`.

#### **Configuration Examples (JSON)**:

1. This example includes users who are staff AND in Milan, but excludes anyone who is inactive OR in the 'Deactivated' group.*
    ```json
    {
      "include": {
        "is_staff": true,
        "custom_fields__office": "Milan"
      },
      "exclude": [
        {"is_active": false},
        {"groups__name": "Deactivated"}
      ]
    }
    ```

2. This example includes users who are in the Milan office OR the Rome office.*
    ```json
    {
      "include": [
        {"custom_fields__office": "Milan"},
        {"custom_fields__office": "Rome"}
      ]
    }
    ```

### External Ruled Filtering (API-driven)
The list of recipients is decided by the external system that triggers the event. Bitcaster will ignore the Distribution List and use the rules provided in the API call.
> **Note**: Like the Dynamic policy, this only targets users with an existing **active Assignment** for the channel.

*   **Best for**: Situations where only the source system knows the exact targets (e.g., "Notify the specific manager of this ticket ID").

---

## 2. Payload Filtering (The "When")

Regardless of the recipient policy, you can define a **Payload Filter** using **JMESPath** syntax. This field supports **YAML** format. If the event data does not match this filter, the notification is skipped.

**Example**: You have a "Server Error" event, but you only want a specific notification to trigger if the error is "Critical".

*   **Filter (YAML)**:
    ```yaml
    severity == 'critical'
    ```
*   **Payload sent to API**: `{"error": "Database down", "severity": "critical"}` -> **Triggered!**
*   **Payload sent to API**: `{"error": "Slow response", "severity": "warning"}` -> **Skipped.**

---

## 3. Extra Context

Notifications can define **Extra Context**, which is a JSON dictionary of static variables. These variables are merged into the template context during message rendering.

This is useful for providing notification-specific information that isn't part of the original event data, such as:
*   Support department contact details.
*   Service Level Agreement (SLA) identifiers.
*   Internal routing labels.

**Example**:
If Extra Context is `{"support_email": "support@example.com"}`, you can use `{{ support_email }}` in your message templates.

---

## 4. API Examples

When triggering an event via API, use the `context` for message data and `options` for routing/filtering.

### Basic Trigger (Standard Policy)
```bash
curl -X POST https://bitcaster.yourdomain.com/api/v1/trigger/my-event/ \
     -H "Authorization: Key YOUR_API_KEY" \
     -d '{
           "context": {"user_count": 50, "status": "ok"}
         }'
```

### Trigger with External Filtering (External Policy)
If your notification is set to **External Ruled Filtering**, you must provide the `filters` inside the `options` object:

```bash
curl -X POST https://bitcaster.yourdomain.com/api/v1/trigger/my-event/ \
     -H "Authorization: Key YOUR_API_KEY" \
     -d '{
           "context": {"ticket_id": 123},
           "options": {
             "filters": {
               "include": {"email": "manager@company.com"}
             }
           }
         }'
```
*Bitcaster will find the user with that email and send the notification only to them, provided they have an active assignment for the channel.*

### Advanced External Filtering (Multiple Users)
```json
{
  "context": {"project": "Bitcaster"},
  "options": {
    "filters": {
      "include": [
        {"groups__name": "developers"},
        {"is_superuser": true}
      ]
    }
  }
}
```
*This example will include users who belong to the 'developers' group OR are superusers.*

---

## Summary Table

| Policy | Source of Truth for Recipients | Format | Scope |
| :--- | :--- | :--- | :--- |
| **None** | Distribution List | N/A | Manual / Static |
| **Subscription** | Direct Subscriptions | N/A | Per-user opt-in |
| **Dynamic** | Database Query | JSON | Automatic / Attribute-based |
| **External** | API Payload | JSON | Real-time / Dynamic |
