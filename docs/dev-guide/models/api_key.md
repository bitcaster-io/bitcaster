# ApiKey

API credential granting programmatic access to the Bitcaster API within an organization, project or application scope.

## Purpose

An ApiKey identifies API clients and authenticates requests using a generated token (`key` field) embedded in Basic Authentication URLs. Records are created by users to obtain credentials for a scope: the key can be limited to an organization, to a project, or to an application (chained foreign keys). The `grants` array defines which operations the key may perform and `environments` restricts which deployment environments the key is valid for. `get_bae()` builds the absolute API URL with the token embedded as the authentication password. The manager's `get_or_create`/`update_or_create` automatically lift the owner chain (application -> project -> organization). Keys inherit the scoped fields from Scoped3Mixin and the audit fields from BitcasterBaseModel.

## Connections

- `user` -> User (on_delete=CASCADE, related_name="keys")
- `organization` -> Organization (on_delete=CASCADE, related_name="api_key_set", inherited from Scoped3Mixin)
- `project` -> Project (ChainedForeignKey on `organization`, on_delete=CASCADE, related_name="api_key_set", blank/null)
- `application` -> Application (ChainedForeignKey on `project`, on_delete=CASCADE, related_name="api_key_set", blank/null)
- Reverse: `keys` on User (ApiKey.user, related_name="keys")
- Reverse: `api_key_set` on Organization, Project and Application (ApiKey scoped fields, related_name="api_key_set")
- unique_together: (`name`, `user`); `key` field is unique

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| name | CharField(255) | no | - | name of his key (db indexed, case-insensitive collation) |
| user | ForeignKey(User) | no | - | user responsible of this key |
| key | CharField(255) | no | generated token (96 chars) | api key (unique) |
| grants | ChoiceArrayField of CharField(255) | yes | - | grants for this key. Options: `FULL_ACCESS` Full Access, `SYSTEM_PING` Ping, `USER_READ` User Read, `USER_PROFILE` Read User Profile and emssages, `USER_WRITE` User Write, `ORG_READ` Organization Read, `APPLICATION_ADMIN` Application Admin, `EVENT_LIST` Event list, `EVENT_TRIGGER` Event Trigger, `EVENT_AUTO_CREATE` Event Auto-Create, `DISTRIBUTION_LIST` Distribution list, `MANAGE_APPLICATION_USERS` Manage Application Users |
| environments | ArrayField of CharField(20) | yes | - | Limit validity to these environments. If empty the key will be valid for any environment |
| organization | ForeignKey(Organization) | no | - | Organization (inherited from Scoped3Mixin) |
| project | ChainedForeignKey(Project) | yes | - | Project this record belong to (inherited from Scoped3Mixin, chained on organization) |
| application | ChainedForeignKey(Application) | yes | - | Application (inherited from Scoped3Mixin, chained on project) |
| version | IntegerVersionField | no | - | version number of the record (inherited from BitcasterBaseModel) |
| last_updated | DateTimeField | no | auto | Record last update time (inherited from BitcasterBaseModel) |
| created | DateTimeField | no | auto | Record creation time (inherited from BitcasterBaseModel) |
