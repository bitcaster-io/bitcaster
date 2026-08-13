# Detailed Process Flow

Bitcaster structure allows to manage simple and complex environments, it is organised as follows:

- <glossary:Organization> (your company)
    - <glossary:Project> (your business domain)
        - <glossary:Application> (the source of your messages)
            - <glossary:Event> (something that happens in your <glossary:Application> that you want to notify to the users)


Each <glossary:Event> can have different <glossary:Channel>s enabled to forward <glossary:Notification>s
to the destination <glossary:Distribution List>

<glossary:Notification> represents the routing and enrichment handler for the event.
It can filter out some event's payload informations or add specific data to be forwarded to the
<glossary:Distribution List>. In this way each event can have multiple Notifications with different filters
and destination recipients.


See the [Glossary](./glossary/index.md) for a list of common Bitcaster terminology
