# Domain Model & Access Control

## Model Hierarchy

```
Organization (owner FK→User)
  └── Project (owner FK→User, org FK→Organization)
       └── Application (owner FK→User, project FK→Project)
            └── Event (application FK→Application, NO owner)
                 └── Notification (event FK→Event)
                 └── Occurrence (event FK→Event)
                 └── Monitor (event FK→Event)
       └── DistributionList (project FK→Project)
       └── Channel (org FK→Organization, optional project)
  └── ApiKey (Scoped3Mixin: org/project/application)
  └── UserRole (user FK→User, org FK→Organization, group FK→Group)
```

## Ownership Cascade

- `Application.save()`: if `owner` unset, falls back to `self.project.owner`
- `Project.save()`: if `owner` unset, falls back to `self.organization.owner`
- The `owner` field is **not enforced as authorization** — no view checks `request.user == obj.owner`

## System Org Protection

- `bitcaster.ORGANIZATION = "OS4D"` is the protected system organisation
- Objects under it: read-only admin fields, deletion blocked, lock/unlock blocked
- Use `.local()` queryset method to exclude system org objects

## API Access Control

- **ApiKeyAuthentication**: `Authorization: Key <token>` header
- **Scope validation** (`ApiApplicationPermission`):
  - URL `org` must match `token.organization.slug`
  - URL `prj` must match `token.project.slug`
  - URL `app` must match `token.application.slug`
- **Grants**: Each view declares `required_grants`, matched against `token.grants`
- **Non-API users**: Only superusers access API without a key

## Admin Access Control

- System org: read-only + no-delete protection
- Hard-coded limits: Organization < 2, Project < 2
- NO per-user queryset filtering — staff users see all data

## Scoped Models

- `Scoped3Mixin` (ApiKey, MessageTemplate): auto-resolves org→project→application cascade on `save()`
- `ScopedManager`: auto-resolves during `get_or_create`/`update_or_create`
- `Channel` uses `ChainedForeignKey` for org→project scoping

## Common Pitfalls

- Creating an Application without a Project (or breaking the FK chain)
- Forgetting `.local()` when querying user-facing objects
- Setting `organization`/`project` directly on a `Scoped3Mixin` model — overwritten on save
- Assuming `owner` field is enforced as authorization
