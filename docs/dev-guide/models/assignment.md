# Assignment

An `Assignment` links an `Address` to a `Channel`, optionally validated and active, and is the recipient unit consumed by the delivery flow.

## Purpose

The `Assignment` is the bridge between a user's `Address` and a delivery `Channel` (email, SMS, etc.), carrying the state that decides whether a notification actually reaches the address: a newly created assignment has `validated=False` and `active=True`. `Address.validate_channel()` flips an assignment to `validated=True`, and the `AddressManager.valid()` queryset filters on `assignments__validated=True`. The `data` JSON field stores system data of the assignment. `DistributionList.recipients` and `Notification` subscriptions both work with `Assignment` records, making it the unit of delivery. `natural_key` is the combination of the `Address` and `Channel` natural keys.

## Connections

- `address` -> `Address` (on_delete=CASCADE, related_name="assignments")
- `channel` -> `Channel` (on_delete=CASCADE, related_name="assignments")
- Reverse: `subscriptions` -> `Subscription` records pointing to this assignment (related_name="subscriptions" on `Subscription.assignment`)
- Reverse: `distributionlist_set` -> `DistributionList` records listing this assignment as a recipient (via `recipients` M2M)
- Unique together: (`address`, `channel`)

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| address | ForeignKey -> Address | No | - | Address to use for this assignment |
| channel | ForeignKey -> Channel | No | - | Channel to assign to the semected address |
| validated | BooleanField | No | False | If the assignment has been validated |
| active | BooleanField | No | True | If the assignment is acive |
| data | JSONField | No | dict | System data of this assignment |
| version | IntegerVersionField | No | - | Version number of the record |
| last_updated | DateTimeField | No | - | Record last update time (auto_now) |
| created | DateTimeField | No | - | Record creation time (auto_now_add) |
