# Notification Policies

In Bitcaster, a **Notification Policy** determines **who** will receive a message when an event is triggered and **under what conditions**. This page is the single reference for recipient policies: every other page that mentions a policy links back here.

When an Event occurs, Bitcaster looks at all the Notifications associated with it. For each notification, it applies two levels of filtering:

1. **Payload Filter**: Should this notification be sent at all based on the data received?
2. **Recipient Policy**: Who are the specific users that should be notified?

---

## 1. Recipient Policies

The policy defines the strategy for selecting recipients. You can choose one of the following options in the Notification settings:

| Admin label | Constant | Recipients are selected from |
| :--- | :--- | :--- |
| **No Filters** (default) | `FILTERING_NONE` | The linked Distribution List |
| **Direct subscriptions** | `FILTERING_SUBSCRIPTION` | Active Subscriptions targeting the notification |
| **API filters** | `FILTERING_EXTERNAL` | Rules provided in the trigger request `options.filters` |
| **Dynamic** | `FILTERING_DYNAMIC` | Stored rules (`recipients_filter`) evaluated against users |

> **Applies to every policy**: delivery always requires the recipient to have an **active Assignment** (address + channel) for one of the event's channels. A user with no active assignment for the channel is never reachable.

---

### No Filters (Distribution List) — `FILTERING_NONE`

This is the default behaviour. The notification is sent to the members of the **Distribution List** linked to the notification.

*   **Best for**: Static teams (e.g., "All System Administrators").
*   **Recipients**: members of the notification's Distribution List who are active users with an active Assignment on the event's channels.
*   **API interaction**:
    *   `limit_to` narrows delivery to list members whose address value appears in the list.
    *   `filters` is **ignored**.
*   A Distribution List is **required** — the notification cannot be saved without one (see [Distribution Lists](dl.md)).

**API payload example** — trigger the event for the whole list:

```bash
curl -X POST 'https://<host>/api/o/{org}/p/{prj}/a/{app}/e/{evt}/trigger/' \
     -H 'Authorization: Key <API_KEY>' \
     -H 'Content-Type: application/json' \
     -d '{
           "context": {"user_count": 50, "status": "ok"}
         }'
```

**API payload example** — send only to the members of the list whose address is `oncall@example.com`:

```bash
curl -X POST 'https://<host>/api/o/{org}/p/{prj}/a/{app}/e/{evt}/trigger/' \
     -H 'Authorization: Key <API_KEY>' \
     -H 'Content-Type: application/json' \
     -d '{
           "context": {"status": "ok"},
           "options": {
             "limit_to": ["oncall@example.com"]
           }
         }'
```

If the address is not a member of the list, nothing is delivered.

---

### Direct Subscriptions — `FILTERING_SUBSCRIPTION`

Recipients are the **Assignments of all active Subscriptions** targeting the notification. Each user can directly subscribe to a Notification using one of their own Assignments, without being a member of any Distribution List.

*   **Best for**: Users who want to opt-in to notifications directly (e.g., "Notify me when a new release is published").
*   **Recipients**: assignments that have an active Subscription to the notification and whose channel is one of the event's channels.
*   **API interaction**:
    *   `limit_to` narrows delivery to subscribed users whose address value appears in the list.
    *   `filters` is **ignored**.
    *   The Distribution List and the stored `recipients_filter` are ignored.
*   Subscriptions are managed in the admin (inline on the **Member** page, like Assignments) or via the [Subscriptions API](../api/subscriptions.md).
*   A user can have multiple Subscriptions to the same Notification as long as the Assignments use **different channels**.

**API payload example** — trigger the event for every active subscriber:

```bash
curl -X POST 'https://<host>/api/o/{org}/p/{prj}/a/{app}/e/{evt}/trigger/' \
     -H 'Authorization: Key <API_KEY>' \
     -H 'Content-Type: application/json' \
     -d '{
           "context": {"release": "v1.2.0"}
         }'
```

**API payload example** — send only to one subscriber, selected by address:

```bash
curl -X POST 'https://<host>/api/o/{org}/p/{prj}/a/{app}/e/{evt}/trigger/' \
     -H 'Authorization: Key <API_KEY>' \
     -H 'Content-Type: application/json' \
     -d '{
           "context": {"release": "v1.2.0"},
           "options": {
             "limit_to": ["john@example.com"]
           }
         }'
```

If `john@example.com` is not an active subscriber, nothing is delivered.

---

### API Filters (External) — `FILTERING_EXTERNAL`

The list of recipients is decided by the external system that triggers the event. Bitcaster ignores the Distribution List and the stored `recipients_filter`, and uses the rules provided in the trigger request's `options.filters`.

*   **Best for**: Situations where only the source system knows the exact targets (e.g., "Notify the specific manager of this ticket ID").
*   **Recipients**: users matching the `include` / `exclude` rules of `options.filters`, with an active Assignment on the event's channels.
*   **API interaction**:
    *   `options.filters` (with `include` / `exclude` rules) drives the selection.
    *   The rules support **Context Variables**: `{ { ... } }` placeholders are rendered with the `context` of the same request.
    *   If `options.filters` is omitted, the notification falls back to *all active users* with an active Assignment on the event's channels.
    *   `limit_to` can be combined to further narrow the selection by address value.
*   The structure of the `filters` object follows the logic described in the [filtering documentation](../dev-guide/filtering.md).

**API payload example** — send only to the user with the given email:

```bash
curl -X POST 'https://<host>/api/o/{org}/p/{prj}/a/{app}/e/{evt}/trigger/' \
     -H 'Authorization: Key <API_KEY>' \
     -H 'Content-Type: application/json' \
     -d '{
           "context": {"ticket_id": 123},
           "options": {
             "filters": {
               "include": {"email": "manager@company.com"},
               "exclude": []
             }
           }
         }'
```

*Bitcaster finds the user with that email and sends the notification only to them, provided they have an active Assignment for the channel.*

**API payload example** — multiple targets with **OR** semantics (users in the `developers` group **or** superusers):

```bash
curl -X POST 'https://<host>/api/o/{org}/p/{prj}/a/{app}/e/{evt}/trigger/' \
     -H 'Authorization: Key <API_KEY>' \
     -H 'Content-Type: application/json' \
     -d '{
           "context": {"project": "Bitcaster"},
           "options": {
             "filters": {
               "include": [
                 {"groups__name": "developers"},
                 {"is_superuser": true}
               ]
             }
           }
         }'
```

**API payload example** — rules driven by request context:

```json
{
    "context": {
        "target_region": "emea"
    },
    "options": {
        "filters": {
            "include": {
                "custom_fields__region": "{{ target_region }}"
            }
        }
    }
}
```

---

### Fixed Ruled Filtering (Dynamic) — `FILTERING_DYNAMIC`

Recipients are selected dynamically from the user database based on specific attributes stored in the notification's **Recipients filter** field.

*   **Best for**: Automatic, attribute-based routing ("Notify everyone in the Milan office").
*   **Recipients**: users matching the stored `recipients_filter` rules, with an active Assignment on the event's channels.
*   **API interaction**:
    *   The stored rules are the only source of truth: `options.filters` provided in the request is **ignored**.
    *   The rules support **Context Variables**: `{ { ... } }` placeholders in the stored filter are rendered with the `context` of the trigger request, so the same notification can route to different users depending on the payload.
    *   `limit_to` can be combined to further narrow the selection by address value.
*   **Format**: the `recipients_filter` field must be valid **JSON**.

#### Using Context Variables in Fixed Rules

When an event is triggered, Bitcaster merges the provided context with the notification settings. You can use any value from this context inside the stored filter.

**Example 1: Filter by a specific username provided in the context**

Store this filter in the notification's **Recipients filter**:

```json
{
  "include": {
    "username": "{{ target_username }}"
  }
}
```

Then trigger the event with the context that drives it:

```bash
curl -X POST 'https://<host>/api/o/{org}/p/{prj}/a/{app}/e/{evt}/trigger/' \
     -H 'Authorization: Key <API_KEY>' \
     -H 'Content-Type: application/json' \
     -d '{
           "context": {"target_username": "john_doe"}
         }'
```

The notification is delivered only to `john_doe`.

**Example 2: Filter by a custom attribute from the context**

Stored filter:

```json
{
  "include": {
    "custom_fields__department": "{{ department_id }}"
  }
}
```

Trigger with `{"department_id": "sales"}` — only users of the sales department are notified.

**Example 3: Complex logic with context**

Stored filter combining multiple context variables and static values:

```json
{
  "include": {
    "is_staff": true,
    "custom_fields__office": "{{ office_name }}",
    "groups__name": "{{ required_group }}"
  }
}
```

**Filter Logic**:

*   **AND**: use a single dictionary. All keys in the dictionary must match.
*   **OR**: use a list of dictionaries. Any dictionary in the list matching will include the user.
*   **Advanced**: a list of lists `[[{}, {}], [{}]]` creates `(OR group) AND (OR group)`.

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

#### Configuration Examples (JSON)

1. This example includes users who are staff AND in Milan, but excludes anyone who is inactive OR in the 'Deactivated' group:

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

2. This example includes users who are in the Milan office OR the Rome office:

    ```json
    {
      "include": [
        {"custom_fields__office": "Milan"},
        {"custom_fields__office": "Rome"}
      ]
    }
    ```

---

## 2. How Policies Interact with Trigger Options

When triggering an event via the API, the `options` object in the request body (`channels`, `environs`, `limit_to`, `filters`) customizes the process on top of the notification's policy:

*   `channels` and `environs` apply to **every** policy: they restrict which channels are used and which environments are targeted.
*   `filters` is honored **only** by the **API Filters** policy (`FILTERING_EXTERNAL`); every other policy ignores it.
*   `limit_to` applies to **every** policy as an **intersection filter**, not an override: it narrows the recipients already selected by the policy to those whose registered address value (email, phone, etc.) appears in the list. If the policy does not reach the user (not in the list, not subscribed, or filtered out), adding `limit_to` does **not** force delivery — the request simply delivers to nobody.

See [Trigger an Event](trigger.md) for the full request reference.

---

## 3. Payload Filtering (The "When")

Regardless of the recipient policy, you can define a **Payload Filter** using **JMESPath** syntax. This field supports **YAML** format. If the event data does not match this filter, the notification is skipped.

**Example**: You have a "Server Error" event, but you only want a specific notification to trigger if the error is "Critical".

*   **Filter (YAML)**:
    ```yaml
    severity == 'critical'
    ```
*   **Payload sent to API**: `{"error": "Database down", "severity": "critical"}` -> **Triggered!**
*   **Payload sent to API**: `{"error": "Slow response", "severity": "warning"}` -> **Skipped.**

See [Event and Notification Filtering](filtering.md) for the full syntax reference.

---

## 4. Extra Context

Notifications can define **Extra Context**, which is a JSON dictionary of static variables. These variables are merged into the template context during message rendering.

This is useful for providing notification-specific information that isn't part of the original event data, such as:

*   Support department contact details.
*   Service Level Agreement (SLA) identifiers.
*   Internal routing labels.

**Example**:

If Extra Context is `{"support_email": "support@example.com"}`, you can use `{{ support_email }}` in your message templates.

---

## 5. Summary Table

| Policy | Source of Truth for Recipients | Trigger `options` honored | Format | Scope |
| :--- | :--- | :--- | :--- | :--- |
| **None** (Distribution List) | Distribution List | `limit_to`, `channels`, `environs` | N/A | Manual / Static |
| **Subscription** | Direct Subscriptions | `limit_to`, `channels`, `environs` | N/A | Per-user opt-in |
| **External** (API filters) | `options.filters` in the request | `filters`, `limit_to`, `channels`, `environs` | JSON | Real-time / Dynamic |
| **Dynamic** | Stored `recipients_filter` | `limit_to`, `channels`, `environs` | JSON | Automatic / Attribute-based |
