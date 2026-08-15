# Address

An `Address` is a communication endpoint (email, phone, account or generic identifier) owned by a `User` that dispatchers use to deliver notifications.

## Purpose

The `Address` model stores the concrete recipient values (an email address, a phone number, etc.) a user wants to be reached at. Records are created when a user registers a new contact point; the `type` field is always derived from the `value` via `AddressManager.get_type_from_value` (both in the manager's `get_or_create` and in `Address.save()`), so a value matching a phone number becomes `PHONE`, one matching an email becomes `EMAIL`, and anything else becomes `GENERIC`. Addresses are linked to `Channel`s through `Assignment` records, which are the objects actually consumed by the notification delivery flow. The `validated` flag that controls deliverability lives on `Assignment`, not on the `Address` itself.

## Connections

- `user` -> `User` (on_delete=CASCADE, related_name="addresses")
- Reverse: `assignments` -> `Assignment` records pointing to this address (related_name="assignments" on `Assignment.address`)
- Reverse: `distributionlist_set` -> `DistributionList` records (via `recipients` M2M to `Assignment`)
- `channels` is a `cached_property` returning the `Channel`s linked through `Assignment` records, not a real relation
- `validate_channel(ch)` creates or updates the `Assignment` for the given channel with `validated=True`
- Unique together: (`user`, `name`) and (`user`, `value`); `natural_key` is (`user.username`, `name`)

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| user | ForeignKey -> User | No | - | Owner of this address |
| name | CharField(255) | No | - | Label or mnemonic name for this address |
| type | CharField(10) | No | GENERIC | Type of address. Choices: `GENERIC` ("Generic address"), `email` ("Email"), `phone` ("Phone"), `account` ("Account") |
| value | CharField(255) | No | - | Specific address value. |
| version | IntegerVersionField | No | - | Version number of the record |
| last_updated | DateTimeField | No | - | Record last update time (auto_now) |
| created | DateTimeField | No | - | Record creation time (auto_now_add) |
