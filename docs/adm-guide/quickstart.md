The following instructions will guide you on how to use the Admin console to set up your first email
[Notification](notification).

For Bitcaster to be able to handle an [Event](event) you must first register it.

Make sure to create records according to the following hierarchy:



Now register a [Channel](channel) with the bitcaster.dispatchers.email.EmailDispatcher [Dispatcher](dispatcher).
Once saved edit the record and use the *configure* button to setup you email server of choice.

Hint: Test the channel! Look for the *test* button on the configured channel in the admin console.
If you do not yet have an _active_ (for the testing purpose, doesn't require to be _validated_) [Assignment](assignment) the admin will propose you add one for your configured
[Addresses](address).

If your test email arrives successfully, it may be a good time to create your first [API key](api-key).
Let's give it at least _ping_, _Event list_, and _Event Trigger_ [Grants](grant).
Remember to keep the key copied somewhere safe as it would be shown only once.

[//]: # (TODO: Assignment Validation feature documention: seams not used... the only part of the code where Assignment.validated is used, AddressManager.valid, is never referenced)

Remember the [Event](event)-[Channel](channel) and the [Assignment](assignment)-[Channel](channel) must match to be
able to receive the [Occurrence](occurrence)

Configure the [Distribution List](distributionlist) for your [Project](project) by selecting the previously configured [Assignment](assignment)

Now it's time to connect all the dots configuring the [Notification](notification) connecting the [Event](event) with the [Distribution List](distributionlist)

Celery Beat process must be up and running in order for the [Occurrence](occurence) to be processed.
Hint: CELERY_TASK_ALWAYS_EAGER is not considered here since the [Occurrence](occurence) processor is scheduled (apply_async() and Task.delay() are not used)
Here an example of how to start it: $`celery -A bitcaster.config.celery worker -E -B --loglevel=DEBUG --concurrency=4`

You may now want to try some APIs. See examples below.

## example requests

- Pinging system

```shell
curl -X 'GET' \
  "${SERVER_URL}/api/system/ping/" \
    -H "accept: application/json" \
    -H "Authorization: Key ${YOUR_API_KEY}"
```

- Get organization details

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
