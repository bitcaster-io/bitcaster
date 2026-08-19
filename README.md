# Bitcaster

[![Test](https://github.com/bitcaster-io/bitcaster/actions/workflows/test.yml/badge.svg)](https://github.com/bitcaster-io/bitcaster/actions/workflows/test.yml)
[![Lint](https://github.com/bitcaster-io/bitcaster/actions/workflows/lint.yml/badge.svg)](https://github.com/bitcaster-io/bitcaster/actions/workflows/lint.yml)
[![security scan](https://github.com/bitcaster-io/bitcaster/actions/workflows/security.yml/badge.svg)](https://github.com/bitcaster-io/bitcaster/actions/workflows/security.yml)
[![GitHub Code Scanning](https://img.shields.io/github/search/bitcaster-io/bitcaster/label%3Asecurity-event?label=security%20issues)](https://github.com/bitcaster-io/bitcaster/security)
[![codecov](https://codecov.io/gh/bitcaster-io/bitcaster/graph/badge.svg?token=kAuZEX5k5o)](https://codecov.io/gh/bitcaster-io/bitcaster)
[![License](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fbitcaster-io%2Fbitcaster%2Fdevelop%2Fpyproject.toml&query=project.license.text&label=license)](https://github.com/bitcaster-io/bitcaster?tab=License-1-ov-file)
[![Docker](https://img.shields.io/docker/pulls/os4d/bitcaster)](https://hub.docker.com/r/os4d/bitcaster/tags)
[![GitHub Release](https://img.shields.io/github/v/release/bitcaster-io/bitcaster)](https://github.com/bitcaster-io/bitcaster/releases)


Bitcaster is a system-to-user **signal-to-message** notification system.

In a usual IT environment, every application must implement multiple protocols to deliver messages to its users (email, SMS, chat, push notifications) — a costly and hard-to-manage problem. Bitcaster moves the notification system from the application layer to the infrastructure layer: it receives signals from any of your applications and systems through a simple RESTful API and converts them into messages distributed across a plethora of channels.

- **Intelligent routing** — payload filtering with JMESPath, dynamic recipient filtering, and environment-aware routing so signals reach exactly the right audience.
- **Flexible templates** — plain text, HTML, and Markdown rendering per channel, with dynamic context injection via a Django-based template engine.
- **Omnichannel delivery** — Email, SMS, Slack, Microsoft Teams, and WebPush through a single REST API.
- **Multi-tenancy & governance** — hierarchical Organizations > Projects > Applications isolation, scoped API keys, SSO (Azure AD, GitHub Enterprise, Google Workspace), and full auditability of every occurrence.
- **User empowerment** — a preference console lets recipients choose how and where they receive each type of message.
- **Operational scalability** — scheduled monitoring agents and a cloud-native Python/Django core built for high-volume signal processing.

## Available Dispatchers

| Dispatcher | Channel |
| --- | --- |
| [AmazonSESDispatcher](https://github.com/bitcaster-io/bitcaster/blob/develop/src/bitcaster/dispatchers/anymail/amazon_ses.py) | Email (Amazon SES) |
| [BrevoDispatcher](https://github.com/bitcaster-io/bitcaster/blob/develop/src/bitcaster/dispatchers/anymail/brevo.py) | Email (Brevo) |
| [EmailDispatcher](https://github.com/bitcaster-io/bitcaster/blob/develop/src/bitcaster/dispatchers/email.py) | Email (SMTP) |
| [GMailDispatcher](https://github.com/bitcaster-io/bitcaster/blob/develop/src/bitcaster/dispatchers/gmail.py) | Email (Gmail) |
| [MailgunDispatcher](https://github.com/bitcaster-io/bitcaster/blob/develop/src/bitcaster/dispatchers/anymail/mailgun.py) | Email (Mailgun) |
| [MailJetDispatcher](https://github.com/bitcaster-io/bitcaster/blob/develop/src/bitcaster/dispatchers/anymail/mailjet.py) | Email (Mailjet) |
| [PostmarkDispatcher](https://github.com/bitcaster-io/bitcaster/blob/develop/src/bitcaster/dispatchers/anymail/postmark.py) | Email (Postmark) |
| [ResendDispatcher](https://github.com/bitcaster-io/bitcaster/blob/develop/src/bitcaster/dispatchers/anymail/resend.py) | Email (Resend) |
| [SendGridDispatcher](https://github.com/bitcaster-io/bitcaster/blob/develop/src/bitcaster/dispatchers/anymail/sendgrid.py) | Email (SendGrid) |
| [SystemDispatcher](https://github.com/bitcaster-io/bitcaster/blob/develop/src/bitcaster/dispatchers/sys.py) | Email (system) |
| [TwilioSMS](https://github.com/bitcaster-io/bitcaster/blob/develop/src/bitcaster/dispatchers/twilio.py) | SMS |
| [SlackDispatcher](https://github.com/bitcaster-io/bitcaster/blob/develop/src/bitcaster/dispatchers/slack.py) | Slack |
| [TeamsDispatcher](https://github.com/bitcaster-io/bitcaster/blob/develop/src/bitcaster/dispatchers/teams.py) | Microsoft Teams |
| [XDispatcher](https://github.com/bitcaster-io/bitcaster/blob/develop/src/bitcaster/dispatchers/x.py) | X (Twitter) |
| [RabbitMQDispatcher](https://github.com/bitcaster-io/bitcaster/blob/develop/src/bitcaster/dispatchers/rabbitmq.py) | Message queue |
| [UserMessageDispatcher](https://github.com/bitcaster-io/bitcaster/blob/develop/src/bitcaster/dispatchers/user_message.py) | In-app user messages |
| [LocalDatabaseDispatcher](https://github.com/bitcaster-io/bitcaster/blob/develop/src/bitcaster/dispatchers/log.py) | Log (local DB, for testing) |

## Getting Started

- [Quick start](https://bitcaster-io.github.io/bitcaster/run/) — install and run Bitcaster
- [Documentation](https://bitcaster-io.github.io/bitcaster/) — full user and admin guides
- [API reference](https://bitcaster-io.github.io/bitcaster/api/) — RESTful signal API
- [Stack samples](https://github.com/bitcaster-io/bitcaster/tree/develop/stack-samples) — ready-to-use deployment examples
- [Docker Hub](https://hub.docker.com/r/os4d/bitcaster/tags) — container images

## Resources

- [Home](https://www.bitcaster.io/)
- [Documentation](https://bitcaster-io.github.io/bitcaster/)
- [Bug Tracker](https://github.com/bitcaster-io/bitcaster/issues)
- [Code](https://github.com/bitcaster-io/bitcaster/)
- [Transifex](https://explore.transifex.com/bitcaster/bitcaster/) (Translate Bitcaster!)
- [License](https://github.com/bitcaster-io/bitcaster/blob/develop/LICENSE.md)
- [Security policy](https://github.com/bitcaster-io/bitcaster/blob/develop/SECURITY.md)

## Contributing

Please read [CONTRIBUTING.md](https://github.com/bitcaster-io/bitcaster/blob/develop/CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.
