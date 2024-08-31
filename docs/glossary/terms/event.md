---
description:  "Something happening in an Application that could be notified to users."
template: term.html
terms:
  - glossary: 
    - Event
---
# Event




When a business operation succeeds or fails, the originated application will send an [Event](event) to Bitcaster with the
related context.

Bitcaster will search all [Notifications](notification) that could match to the [Event](event)
(depending on the [Notification](notification) _payload_filter_)
