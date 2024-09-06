The following instructions will guide you on how to use the Admin console to set up your first email
<glossary:Notification>.

For Bitcaster to be able to handle an <glossary:Event> you must first register it.

1. Create your Organization/Project [structure](structure.md)
2. Navigate to <https://SERVER_ADDRESS/admin/bitcaster/channel/add/>

Now register a <glossary:Channel> with the `bitcaster.dispatchers.email.EmailDispatcher` <glossary:Dispatcher>.
Once saved edit the record and use the *configure* button to setup you email server of choice.

Hint: Test the channel! Look for the *Test* button on the configured channel in the admin console.
If you do not yet have an _active_ (for the testing purpose, doesn't require to be _validated_) <glossary:Assignment> the admin will propose you add one for your configured
<glossary:Address>.

If your test email arrives successfully, it may be a good time to create your first <glossary:API Key>.
Let's give it at least _ping_, _Event list_, and _Event Trigger_ <glossary:Grant>.
Remember to keep the key copied somewhere safe as it would be shown only once.

[//]: # (TODO: Assignment Validation feature documention: seams not used... the only part of the code where Assignment.validated is used, AddressManager.valid, is never referenced)

Remember the <glossary:Event>-<glossary:Channel> and the <glossary:Assignment-<glossary:Channel> must match to be
able to receive the <glossary:Occurrence>

Configure the <glossary:Distribution List> for your <glossary:Project> by selecting the previously configured <glossary:Assignment>

Now it's time to connect all the dots configuring the <glossary:Notification> connecting the <glossary:Event> with the <glossary:Distribution List>

Last but not least, configure a <glossary:Message> for your <glossary:Notification>.
After first save, you will be able to modify your template using an enhanced editor by clicking the *Edit* button 

Celery Beat process must be up and running in order for the <glossary:Occurrence> to be processed.
Hint: CELERY_TASK_ALWAYS_EAGER is not considered here since the <glossary:Occurrence> processor is scheduled (apply_async() and Task.delay() are not used)
Here an example of how to start it: $`celery -A bitcaster.config.celery worker -E -B --loglevel=DEBUG --concurrency=4`

You may now want to try some APIs. See examples below.

## Example requests

- Pinging system

```shell
curl -X 'GET' \
  "[SERVER_ADDRESS]/api/system/ping/" \
    -H "accept: application/json" \
    -H "Authorization: Key ${YOUR_API_KEY}"
```

- Get organization details

```shell
curl -X 'GET' "[SERVER_ADDRESS]/api/o/${ORG_SLUG}/" \
    -H "accept: application/json" \
    -H "Authorization: Key ${YOUR_API_KEY}"
```

- Trigger an event

```shell
curl -X 'POST' "[SERVER_ADDRESS]/api/o/${ORG_SLUG}/p/${PROJECT_SLUG}/a/${APP_SLUG}/e/${EVENT_SLUG}/trigger/" \
    -H "accept: application/json" \
    -H "Authorization: Key ${YOUR_API_KEY}"
```
