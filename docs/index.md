---
title: Documentation
---
<div class="align-center">
<img src="https://www.bitcaster.io/wp-content/uploads/2024/06/bitcaster-logo-h2.svg">
</div>

# Welcome to Bitcaster Documentation

Bitcaster is a system-to-user signal-to-message notification system.


In a usual IT environment, Applications must send specific messages to their users. Usually, each application needs to implement multiple protocols to allow users to receive information differently (email, SMS). This can be problematic, expensive, and difficult to manage.


Bitcaster aims to handle these situations by moving the notification system from the application layer to the infrastructure layer.



Bitcaster will receive signals from any of your applications/systems using a simple RESTful API and will convert them in messages to be distributed to you users via a plethora of channels.


Messages content is customised at user/receiver level using a flexible template system.


Your user will be empowered with an easy to use console to choose how to receive the messages configured in Bitcaster.


### Structure


Bitcaster structure allows to manage simple and complex environment, it is organised as follow:


- <glossary:Organization> (your company)

    - <glossary:Project> (your business domain)

        - <glossary:Application> (the source of your messages)

            - <glossary:Event> (something that happen in your <glossary:Application> that you want to notify to the users)



Each <glossary:Event> can have different <glossary:Channel>s enabled to forward <glossary:Notification>s 
the destination <glossary:Distribution List> 



See the [Glossary](./glossary/index.md) for a list of common Bitcaster terminology

[//]: # ()
[//]: # (---)

[//]: # (<div class="text-center">)

[//]: # (<a href="getting-started/" class="btn btn-primary" role="button">Getting Started</a>)

[//]: # (<a href="user-guide/" class="btn btn-primary" role="button">User Guide</a>)

[//]: # (</div>)
