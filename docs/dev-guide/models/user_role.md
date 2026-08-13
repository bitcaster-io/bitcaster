# UserRole

The `UserRole` assigns a `Group` to a `User` within an `Organization`, scoping role membership per tenant.

## Purpose

A user's role is meaningful only inside an organization: this model ties the three together and is unique per (organization, user, group) combination. Records are created by `Organization.enroll_users()`, which bulk-creates a `UserRole` for every user (excluding the built-in system user) with the default group, and by the admin. The `Organization.users` property and the `User.organizations` property are both resolved through this model's reverse/forward relations, and `natural_key()` is (group name, username, organization slug).

## Connections

- `user` -> User (on_delete=CASCADE, related_name="roles")
- `organization` -> Organization (on_delete=CASCADE, no explicit related_name)
- `group` -> Group (on_delete=CASCADE, no explicit related_name)
- Unique together: (`organization`, `user`, `group`)

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| user | ForeignKey(User) | No | - | user the role is assigned to |
| organization | ForeignKey(Organization) | No | - | organization the role belongs to |
| group | ForeignKey(Group) | No | - | group granting the role |
| version | IntegerVersionField from BitcasterBaseModel | No | 0 | version number of the record |
| last_updated | DateTimeField (auto_now) from BitcasterBaseModel | No | auto | Record last update time |
| created | DateTimeField (auto_now_add) from BitcasterBaseModel | No | auto | Record creation time |
