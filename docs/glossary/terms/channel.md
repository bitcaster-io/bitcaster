---
description:  Is the target system that will forward the Message to the Recipient
template: term.html
terms:
    - glossary:
      - Channel
      - Abstract Channel
      - Project Channel
tags:
  - channel

---
# Channel

it represents a way of communicating with users sending custom  <glossary:Message> 
to <glossary:Distribution List>

Bitcaster knows two type of channels:

#### Abstract Channels

These channels are created at Organization level, they cannot be used directly until not
    directly referenced by a Project Channel


#### Project Channels

Project channel can be used to by the project's applications to forward messages.
They can be created from scratch ot inherit from an `Abstract Channels` 

Only project-level Channels can be used to send <glossary:Notification>.
