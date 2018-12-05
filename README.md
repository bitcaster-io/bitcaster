# Bitcaster

[![circle-build]][circle-link]
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/6fa79049ba7c44dd9b082a7ed8b5dce9)](https://www.codacy.com/app/bitcaster/bitcaster?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bitcaster-io/bitcaster&amp;utm_campaign=Badge_Grade)
[![codecov-badge]][codecov]
[![](https://images.microbadger.com/badges/version/bitcaster/demo.svg)](https://microbadger.com/images/bitcaster/demo "Get your own version badge on microbadger.com")
[![pypi-version]][pypi] 

<p align="center">
 <p align="center">
   <img src="https://raw.githubusercontent.com/bitcaster-io/bitcaster/develop/src/bitcaster/static/bitcaster/images/bitcaster500.png" alt="Bitcaster" height="128">
 </p>
 <p align="center">
   <i>Broadcast your bits!</i>
 </p>
</p>

## What's Bitcaster

Bitcaster is a system-to-user signal-to-message notification system.

Bitcaster will receive signals from any of your applications/systems using a simple RESTful API and will convert them in messages to be distributed to you users via a plethora of channels.

Messages content is customised at user/receiver level using a flexible template system.

Your user will be empowered with an easy to use console to choose how to receive the messages configured in Bitcaster.

Bitcaster comes loaded with all of the following channel plugins:
* Facebook
* Gmail
* Hangout
* skype
* slack
* twitter
* SMS (Plivo, Twilio)

In addition a plugin SDK will allow you to create your own plugins in order to extend the reach of your signals to any possible conceivable target. 

## Resources

**Bug Tracker** https://github.com/bitcaster-io/bitcaster/issues

**Code** https://github.com/bitcaster-io/bitcaster

**Transifex** https://www.transifex.com/sax9/bitcaster/(Translate Bitcaster!)

**Docker** https://hub.docker.com/r/bitcaster/


[travis-build]:https://secure.travis-ci.org/bitcaster-io/bitcaster.png?branch=develop
[travis-link]: https://travis-ci.org/bitcaster-io/bitcaster?branch=develop
[circle-build]: https://circleci.com/gh/bitcaster-io/bitcaster.svg?style=svg
[circle-link]: https://circleci.com/gh/bitcaster-io/bitcaster

[codecov-badge]: https://codecov.io/gh/bitcaster-io/bitcaster/branch/develop/graph/badge.svg
[codecov]: https://codecov.io/gh/bitcaster-io/bitcaster

[pypi-version]: https://img.shields.io/pypi/v/bitcaster.svg
[pypi]: https://pypi.org/project/bitcaster/
