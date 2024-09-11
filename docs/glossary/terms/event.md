---
description:  "Something happening in an Application that could be notified to users."
template: term.html
terms:
  - glossary: 
    - Event
    - trigger url
---
# Event




When a business operation succeeds or fails, the originated application will send an <glossary:Event> to Bitcaster with the
related context.

Bitcaster will search all <glossary:Notification> that could match to the <glossary:Event>
(depending on the <glossary:Notification> _payload_filter_)


### Trigger URL

Each Event has an unique `trigger url` that can be seen on the top-left of the details page.
Trigger url is compose as:

```
[SERVER_ADDRESS]/o/[organization]/p/[project]/a/[application]/e/[event]/trigger
```
