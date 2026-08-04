---
description:  "the message sent to a Recipient as result of an Occurrence"
template: term.html
terms:
  - glossary:
    - Delivery
---
# Delivery

A Delivery is the single message sent to a <glossary:Recipient> as result of an <glossary:Occurrence>.

When an Occurrence is processed, one Delivery is created for each recipient. The message content is
rendered and snapshotted at that time. Deliveries are then dispatched in background, with automatic
retry in case of errors.

Missing message templates produce failed deliveries and are never retried.
