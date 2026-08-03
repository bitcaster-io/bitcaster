---
tags:
   - Address

---
# Manage Addresses

An <glossary:Address> is a delivery endpoint of a user: an email, a phone
number or any value that a <glossary:Channel> can reach.

## Address list

The address list at <https://SERVER_ADDRESS/admin/bitcaster/address/> shows the
user each address belongs to, its name, value and type. Use the search box to
find an address by name or value and filter by user or type.

## Add or edit an address

1. Select the **user** the address belongs to
1. Provide a **name** (e.g. `work email`) and the **value** (e.g.
   `john@example.com`)
1. Choose the **type** of address (email, phone, ...)

## Validate and assign to a channel

An address must be validated before it can be used: select the address and use
the **Assign to channel** action to pick the <glossary:Channel> and the
distribution or notification it is validated for.

Validated addresses are used by <glossary:Assignment>s as the destination of
the message.
