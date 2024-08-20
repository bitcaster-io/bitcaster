# Welcome to Bitcaster Documentation

Bitcaster is a system-to-user signal-to-message notification system.

In a usual IT environment, Applications must send specific messages to their users. Usually, each application needs to implement multiple protocols to allow users to receive information differently (email, SMS). This can be problematic, expensive, and difficult to manage.

Bitcaster aims to handle these situations by moving the notification system from the application layer to the infrastructure layer.


Bitcaster will receive signals from any of your applications/systems using a simple RESTful API and will convert them in messages to be distributed to you users via a plethora of channels.

Messages content is customised at user/receiver level using a flexible template system.

Your user will be empowered with an easy to use console to choose how to receive the messages configured in Bitcaster.

### Structure

Bitcaster structure allows to manage simple and complex environment, it is organised as follow:

- [Organization](organization) (your company)
    - [Project](project) (your business domain)
        - [Application](application) (the source of your messages)
            - [Event](event) (something that happen in your [Application](application) that you want to notify to the users)


Each [Event](event) can have different [Channels](channel) enabled to forward [Notifications](notification) 
the destination [Distribution List](distribution-list) 


See the [Glossary](./glossary/index.md) for a list of common Bitcaster terminology
