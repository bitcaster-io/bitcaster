# Filtering

This module provides a flexible way to filter Recipients using a JSON-like structure. It allows you to define complex filtering logic with `AND` and `OR` conditions, which can be easily serialized and stored.

## `FilterManager[M]`

The main class in this module. It takes a Django `QuerySet` or `Manager` and a filter specification, and applies the specified filters.

!!! note "Template Rendering"
    While `FilterManager` itself does not handle template rendering, the `Notification` model implements a `render_recursive` helper that processes any Jinja2-style `{{ ... }}` placeholders in the filter dictionary using the event context before passing it to the `FilterManager`.

**Arguments:**

*   `queryset` (`QuerySetOrManager[M]`): The Django `QuerySet` or `Manager` to be filtered.
*   `filter_spec` (`QuerysetFilter`): A dictionary defining the filtering logic. It should have two optional keys: `include` and `exclude`.

**Methods:**

*   `filter(*args, **kwargs) -> QuerySet[M]`: Applies the filters defined in `filter_spec` to the `queryset` and returns the filtered `QuerySet`.

---

## Filter Specification (`filter_spec`)

The `filter_spec` is a dictionary that defines the filtering logic. It can contain two keys:

*   `include`: A list of conditions that records must match (an `AND` operation between groups).
*   `exclude`: A list of conditions that records must not match.

The structure of `include` and `exclude` can be one of the following:

1.  **A single dictionary**: Represents a single `AND` condition.
    ```json
    {"username": "user1", "email": "a@b.com"}
    ```
    *SQL: WHERE username = 'user1' AND email = 'a@b.com'*

2.  **A list of dictionaries**: Represents a group of `OR` conditions.
    ```json
    [{"username": "user1"}, {"username": "user2"}]
    ```
    *SQL: WHERE username = 'user1' OR username = 'user2'*

3.  **A list of lists of dictionaries**: Represents an `AND` operation between `OR` groups.
    ```json
    [
        [{"username": "user1"}, {"username": "user2"}],
        [{"is_active": True}]
    ]
    ```
    *SQL: WHERE (username = 'user1' OR username = 'user2') AND is_active = True*

---

## Usage Samples

Here are some examples of how to use the `FilterManager`:

### Sample 1: Simple `include` filter

This example filters for users with the username "user1".

```python
from django.contrib.auth.models import User
from bitcaster.utils.filering import FilterManager

# Filter for users with the username 'user1'
filter_spec = {
    "include": {"username": "user1"}
}

# Assuming you have a User model
queryset = User.objects.all()
filtered_users = FilterManager(queryset, filter_spec).filter()

# This is equivalent to:
# User.objects.filter(username="user1")
```

### Sample 2: `include` filter with `OR` condition

This example filters for users whose username is either "user1" or "user2".

```python
from django.contrib.auth.models import User
from bitcaster.utils.filering import FilterManager

# Filter for users with username 'user1' OR 'user2'
filter_spec = {
    "include": [{"username": "user1"}, {"username": "user2"}]
}

queryset = User.objects.all()
filtered_users = FilterManager(queryset, filter_spec).filter()

# This is equivalent to:
# from django.db.models import Q
# User.objects.filter(Q(username="user1") | Q(username="user2"))
```

### Sample 3: Complex `include` filter with `AND` and `OR` conditions

This example filters for active users whose username is either "user1" or "user2".

```python
from django.contrib.auth.models import User
from bitcaster.utils.filering import FilterManager

# Filter for active users with username 'user1' OR 'user2'
filter_spec = {
    "include": [
        [{"username": "user1"}, {"username": "user2"}],
        [{"is_active": True}]
    ]
}

queryset = User.objects.all()
filtered_users = FilterManager(queryset, filter_spec).filter()

# This is equivalent to:
# from django.db.models import Q
# User.objects.filter(
#     (Q(username="user1") | Q(username="user2")) & Q(is_active=True)
# )
```

### Sample 4: `include` and `exclude` filters

This example filters for all active users but excludes those with the username "admin".

```python
from django.contrib.auth.models import User
from bitcaster.utils.filering import FilterManager

# Filter for all active users, but exclude the user 'admin'
filter_spec = {
    "include": {"is_active": True},
    "exclude": {"username": "admin"}
}

queryset = User.objects.all()
filtered_users = FilterManager(queryset, filter_spec).filter()

# This is equivalent to:
# User.objects.filter(is_active=True).exclude(username="admin")
```
