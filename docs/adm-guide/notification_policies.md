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

### Fixed Ruled Filtering (Dynamic)
Recipients are selected dynamically from the user database based on specific attributes.
> **Note**: This policy only selects from users who have an **active Assignment** (configured address) for the channel being used.

*   **Format**: This field must be valid **JSON**.
*   **Filter Logic**:
    *   A single dictionary `{}` applies **AND** between its keys.
    *   A list of dictionaries `[{}]` applies **OR** between the dictionaries.
    *   A list of lists `[ [{}], [{}] ]` applies **AND** between the inner groups.
*   **Configuration Example (JSON)**:
    ```json
    {
      "include": {
        "is_staff": true,
        "metadata__office": "Milan"
      },
      "exclude": {
        "is_active": false
      }
    }
    ```
*   **Best for**: Targeting users based on global attributes (e.g., "All users in Italy").

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

## 3. API Examples

When triggering an event via API, use the `context` for message data and `options` for routing/filtering.

### Basic Trigger (Standard Policy)
```bash
curl -X POST https://bitcaster.yourdomain.com/api/v1/trigger/my-event/ \
     -H "Authorization: Token YOUR_API_KEY" \
     -d '{
           "context": {"user_count": 50, "status": "ok"}
         }'
```

### Trigger with External Filtering (External Policy)
If your notification is set to **External Ruled Filtering**, you must provide the `filters` inside the `options` object:

```bash
curl -X POST https://bitcaster.yourdomain.com/api/v1/trigger/my-event/ \
     -H "Authorization: Token YOUR_API_KEY" \
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
| **Dynamic** | Database Query | JSON | Automatic / Attribute-based |
| **External** | API Payload | JSON | Real-time / Dynamic |
