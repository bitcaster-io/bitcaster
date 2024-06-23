The following instructions will guide you how to use the Admin console to setup your first email [Notification](notification).

For Bitcaster to be able to handle an [Event](event) you must first register it.

Make sure to create records according to the following hierarchy:

- [Organization](organization)
      - [Project](project)
        - [Application](application)
            - [Event](event)

Now register a [Channel](channel) with the bitcaster.dispatchers.email.EmailDispatcher [Dispatcher](dispatcher).
Once saved edit the record and use the *configure* button to setup you email server of choice.

Hint: Now could be a good time to test the channel. Look for the *test* button. If you do not yet have a
_validated_ [Assignment](assignment) the admin will propose you add one for your configured [Addresses](address).