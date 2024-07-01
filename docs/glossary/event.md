any business event originated in the source system tha will be forwarded to the [Recipient](recipient).

When a business operation succeed or fail the originated system will send an [Event](event) to Bitcaster with the
related context.
Bitcaster will search all [Notifications](notification) that could match to the [Event](event)
(depending on the [Notification](notification) _payload_filter_)
