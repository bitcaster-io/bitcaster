# Event and Notification Filtering

Bitcaster provides a powerful filtering engine that allows you to control exactly **when** a notification should be sent based on the data received during an event trigger.

Filtering is defined using **JMESPath** syntax, which can be applied directly as a string or wrapped in structured **YAML** blocks for complex logic.

---

## Simple Filtering (JMESPath)

The most common way to filter is by providing a JMESPath expression in the **Payload Filter** field of a Notification.

### Basic Examples

| Goal | Filter Expression            |
| :--- |:-----------------------------|
| Match a string | `country == 'italy'`         |
| Match a number | `office == 22`               |
| Check nested data | `server.status == 'down'`    |
| Check if field exists | `attribute_not_null(urgent)` |

> **Note on Numbers**: In JMESPath, literal numbers must be enclosed in backticks (e.g., `` `22` ``) to be treated as integers rather than strings.

---

## Complex Logic (Structured YAML)

When you need to combine multiple conditions, you can use a structured YAML syntax. Bitcaster supports `AND`, `OR`, and `NOT` operators.

### AND Operator
All conditions must be true.
```yaml
AND:
  - country == 'italy'
  - area == 'europe'
```

### OR Operator
At least one condition must be true.
```yaml
OR:
  - country == 'italy'
  - office == 22
```

### Nested Logic
You can nest these operators to create highly specific rules.

**Goal**: Notify if (Country is Italy AND Region is Lazio) OR if the Office ID is 22.
```yaml
OR:
  - AND:
      - area == 'europe'
      - country == 'italy'
  - office == 22
```

---

## How it works with the API

When you trigger an event via the API, the filtering engine evaluates your rules against the `context` object provided in the request.

### Example Request
```json
{
    "context": {
        "area": "europe",
        "country": "italy",
        "office": 10,
        "message": "High temperature alert"
    }
}
```

If a notification has the filter `country == 'italy' && area == 'europe'`, it will be **processed** because both conditions match the context.

---

## Testing your Filters

It is recommended to test your JMESPath expressions using the [JMESPath Tutorial](https://jmespath.org/tutorial.html) or online testers before deploying them to production.

Common pitfalls to watch out for:
*   **Case Sensitivity**: `'italy'` is different from `'Italy'`.
*   **Quotes**: Use single quotes `'` for strings.
*   **Backticks**: Use backticks `` ` `` for numbers, booleans (`true`/`false`), and nulls.
