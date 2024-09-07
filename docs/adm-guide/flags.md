---
tags:
    - flags
---

# Feature Flag Conditions

!!! hint

    You can use `FLAG_CONDITION_TEST` flag to test your conditions.



### Environment Variable

Use this to check environment variables. 
It can be used to check for the variable value (using `=`) or just checking for its presence

Es.

    BITCASTER_LOGGING_LEVEL=CRITICAL
    BITCASTER_LOGGING_LEVEL


### User IP

Check if remote User IP is equal the value or belong a network/subnet

Es:
    
    192.168.10.1
    192.168.10.0/24

### Boolean

Hard Enable/Disable Flag 

Es:

    True
    False
    1
    0


### Development mode

True if `DEBUG=True` and Bitcaster is running on local machine

!!! note

    This condition does not expect value.


### Server Address

Enable the flag if the Bitcaster IP is equal to the value

### User

Valid when the current user's username is equal to the provided value.

Es:

    admin@bitcaster.io

!!! warning

    In case you should make some mistake that prevent you to access Bitcaster, you can use the command
    line to enable/dosable flags. Just type this in the console

        django-admin enable_flag [FLAG_NAME] [FLAG_VALUE]
    or
        
        django-admin disable_flag [FLAG_NAME] [FLAG_VALUE]


### HTTP Request Header

Enable Flag based on custom HTTP Request headers. All 'received' headers are normalised as:

- Replace hyphen `-` with underscore `_`
- Converted to UPPERCASE.

Value can be a valid python regex

Es:

    USER_AGENT=
    USER_AGENT=Mozilla
    USER_AGENT=.*Macintosh
