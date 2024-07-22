The following instructions will guide you on how to use the Admin console to set up your first email
[Notification](notification).

For Bitcaster to be able to handle an [Event](event) you must first register it.

Make sure to create records according to the following hierarchy:

- [Organization](organization)
      - [Project](project)
        - [Application](application)
            - [Event](event)

Now register a [Channel](channel) with the bitcaster.dispatchers.email.EmailDispatcher [Dispatcher](dispatcher).
Once saved edit the record and use the *configure* button to setup you email server of choice.

Hint: Now is a good time to test the channel. Look for the *test* button on the configured channel in the admin
console.
If you do not yet have a _validated_ [Assignment](assignment) the admin will propose you add one for your configured
[Addresses](address).

If your test email arrives successfully, it may be a good time to create your first [API key](api-key).
Let's give it at least _ping_, _Event list_, and _Event Trigger_ [Grants](grant).
Remember to keep the key copied somewhere safe as it would be shown only once.

You may now want to try some APIs. See examples below.

Remember the [Event](event) [Channel](channel) and the [Assignment](assignment) [Channel](channel) must match to be
able to receive the [Occurrence](occurrence)

## example requests

- Pinging system

```shell
curl -X 'GET' \
  '${SERVER_URL}/api/system/ping/' \
    -H "accept: application/json" \
    -H "Authorization: Key ${YOUR_API_KEY}"
```

- Get organisation details

```shell
curl -X 'GET' "${SERVER_URL}/api/o/${ORG_SLUG}/" \
    -H "accept: application/json" \
    -H "Authorization: Key ${YOUR_API_KEY}"
```

- Trigger an event

```shell
curl -X 'POST' "${SERVER_URL}/api/o/${ORG_SLUG}/p/${PROJECT_SLUG}/a/${APP_SLUG}/e/${EVENT_SLUG}/trigger/" \
    -H "accept: application/json" \
    -H "Authorization: Key ${YOUR_API_KEY}"
```
