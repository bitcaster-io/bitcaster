# Group

The `Group` is a proxy model over the Django auth `Group` used to grant named roles inside an organization.

## Purpose

A group has no extra fields or behavior: it is the `bitcaster.Group` proxy of `django.contrib.auth.models.Group`, present so the platform can reference the auth group type in its own app. Groups are created from the admin and are assigned to users through `UserRole` records (`Organization.enroll_users()` assigns a group to every enrolled user), which is how permissions are aggregated per organization.

## Connections

- `permissions` -> Permission (ManyToManyField, on_delete=CASCADE, blank)
- Reverse: `user_set` -> User (from User.groups ManyToManyField), `userrole_set` -> UserRole (UserRole.group)
- `name` is implicitly unique on the underlying auth Group table

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| id | BigAutoField | No | auto | primary key (inherited from Django auth Group) |
| name | CharField(max_length=150) | No | - | group name, unique (inherited from Django auth Group) |
| permissions | ManyToManyField(Permission) | No (blank) | - | permissions held by this group (inherited from Django auth Group) |
