# SocialProvider

Configuration of a social login provider (OAuth/OIDC) used for authentication.

## Purpose

The SocialProvider stores the credentials and settings needed to enable a social login provider in the system: provider type (selected from the django-allauth provider registry), client id, secret, optional extra key, and provider-specific extra configuration as JSON. Records are created when an administrator enables a social login option. `save()` defaults the label to the provider value when empty and the manager's `as_choices()` returns the enabled providers as `(pk, label)` choices.

## Connections

- No ForeignKey fields
- No reverse relations
- Unique constraints: `label` is unique; UniqueConstraint `unique_client_provider` on (client_id, provider)

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| label | CharField(50) | No | None | Label (unique) |
| provider | CharField(30) | No | None | Social Login provider (options from the allauth provider registry) |
| client_id | CharField(191) | No | "" | App ID or Client ID (blank allowed) |
| secret | CharField(191) | No | "" | API Secret or Client Secret (blank allowed) |
| key | CharField(191) | No | "" | Optional extra key (if required by provider) (blank allowed) |
| configuration | JSONField | No | dict | Extra provider-specific settings |
| enabled | BooleanField | No | True | Provider status |
