---
tags:
   - Member

---
# Manage Members

Members are the users that belong to your organization. Membership is what
gives a user a role in the organization and makes them a potential recipient
of its notifications: a user can be member of multiple organizations with a
different role in each.

## Member list

The member list at <https://SERVER_ADDRESS/admin/bitcaster/member/> shows all
users and the organization they belong to.

## Member detail

Open a member to manage:

- **Addresses** — the addresses (email, phone, ...) of the user; each address
  can be validated and assigned to a channel
- **Assignments** — the <glossary:Assignment>s of the user: which address is
  used on which <glossary:Channel> and whether it is active
- **Subscriptions** — the notifications the user subscribed to directly
- **Distribution lists** — the <glossary:Distribution List>s the member belongs to
- **Groups and roles** — permissions assigned to the user

## Import members

Use the **Import members** action to bulk-create members from a CSV file
instead of adding them one by one. The import supports the name, username and
email columns and reports the errors found in the file.
