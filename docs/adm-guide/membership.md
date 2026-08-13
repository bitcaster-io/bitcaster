# Manage Application Memberships

An **Application Membership** is the per-application relationship between a
<glossary:User> and an <glossary:Application>: it tells Bitcaster whether the
user belongs to the application and may receive notifications from it.

Members are usually created and removed by the remote system through the
application `register` and `unregister` APIs. The membership page lets you
inspect and fine-tune those memberships from the admin.

## Membership list

The list at <https://SERVER_ADDRESS/admin/bitcaster/applicationmembership/>
shows a row per membership with the `User`, `Application`, `Active`, `Locked`
and `Enable notifications` columns. Use the search box to find memberships by
username and filter by user, application, active, locked or notifications
state.

## Edit a membership

Open a membership to see its fields:

- `User`: the member user.
- `Application`: the application the user is member of.
- `Custom fields`: per-application member data provided by the remote
  system.
- `Active`: mirrors the client application "active" state for the user. If
  unchecked, the user receives no notifications for this application.
- `Locked`: the membership is managed only via the admin. If checked, no
  notification is sent to the user for this application.
- `Enable notifications`: whether the user receives notifications for this
  application (effective only when the membership is active and not locked).

A user receives notifications from an application only when all three
conditions hold. See the <glossary:Application Member> glossary entry for the
API-side behaviour.
