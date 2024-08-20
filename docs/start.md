# Detailed PRocess Flow




Bitcaster structure allows to manage simple and complex environment, it is organised as follow:

- [Organization](organization) (your company)
    - [Project](project) (your business domain)
        - [Application](application) (the source of your messages)
            - [Event](event) (something that happen in your [Application](application) that you want to notify to the users)


Each [Event](event) can have different [Channels](channel) enabled to forward [Notifications](notification) 
the destination [Distribution List](distribution-list) 


See the [Glossary](./glossary/index.md) for a list of common Bitcaster terminology
