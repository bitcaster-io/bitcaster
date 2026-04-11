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
Recipients are selected dynamically from the entire user database based on specific attributes (e.g., role, location, or custom tags).
*   **Configuration Example (YAML)**:
    ```yaml
    # Filter users who are staff and in the 'Milan' office
    AND:
      - "is_staff == `true`"
      - "metadata.office == 'Milan'"
    ```
*   **Best for**: Global attributes that change frequently.

### External Ruled Filtering (API-driven)
The list of recipients is decided by the external system that triggers the event. Bitcaster will ignore the Distribution List and use the rules provided in the API call.
*   **Best for**: Situations where only the source system knows the exact targets (e.g., "Notify the specific manager of this ticket ID").

### Context Based Filtering
The notification is enabled or disabled based on values within the event context. It usually still targets a Distribution List but adds a conditional "Go/No-Go" check.

---

## 2. Payload Filtering (The "When")

Regardless of the recipient policy, you can define a **Payload Filter** using **JMESPath** syntax. If the event data does not match this filter, the notification is skipped.

**Example**: You have a "Server Error" event, but you only want a specific notification to trigger if the error is "Critical".

*   **Filter**: `severity == 'critical'`
*   **Payload sent to API**: `{"error": "Database down", "severity": "critical"}` -> **Triggered!**
*   **Payload sent to API**: `{"error": "Slow response", "severity": "warning"}` -> **Skipped.**

---

## 3. API Examples

When triggering an event via API, the `pk` or `slug` of the event is used.

### Basic Trigger (Standard Policy)
```bash
curl -X POST https://bitcaster.yourdomain.com/api/v1/trigger/my-event/ \
     -H "Authorization: Token YOUR_API_KEY" \
     -d '{"user_count": 50, "status": "ok"}'
```

### Trigger with External Filtering (External Policy)
If your notification is set to **External Ruled Filtering**, you must provide the `filter` in the request:

```bash
curl -X POST https://bitcaster.yourdomain.com/api/v1/trigger/my-event/ \
     -H "Authorization: Token YOUR_API_KEY" \
     -d '{
           "data": {"ticket_id": 123},
           "filter": "email == 'manager@company.com'"
         }'
```
*Bitcaster will find the user with that email and send the notification only to them.*

### Advanced External Filtering (Multiple Users)
```json
{
  "data": {"project": "Bitcaster"},
  "filter": {
    "OR": [
      "groups.contains('developers')",
      "is_superuser == `true`"
    ]
  }
}
```

---

## Summary Table

| Policy | Source of Truth for Recipients | Complexity |
| :--- | :--- | :--- |
| **None** | Distribution List (Manual) | Low |
| **Dynamic** | Database Query (Automatic) | Medium |
| **External** | API Payload (Real-time) | High |
| **Context** | Context values + Dist. List | Medium |
