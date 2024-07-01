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



## example requests

- Pinging system

```shell
curl -X 'GET' \
  'http://<host>:8000/api/system/ping/' \
  -H 'accept: application/json' \
  -H 'Authorization: Key <your API key here>'
```

- Get organisation details

```shell
curl -X 'GET' \
  'http://<host>:8000/api/o/<organisation slug here>/' \
  -H 'accept: application/json' \
  -H 'Authorization: Key <your API key here>'
```

- Get organisation details

```shell
curl -X 'GET' \
  'http://<host>:8000/api/o/<organisation slug here>/' \
  -H 'accept: application/json' \
  -H 'Authorization: Key <your API key here>'
```

