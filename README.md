# bitcaster


[![Test](https://github.com/bitcaster-io/bitcaster/actions/workflows/test.yml/badge.svg)](https://github.com/bitcaster-io/bitcaster/actions/workflows/test.yml)
[![Lint](https://github.com/bitcaster-io/bitcaster/actions/workflows/lint.yml/badge.svg)](https://github.com/bitcaster-io/bitcaster/actions/workflows/lint.yml)
[![security scan](https://github.com/bitcaster-io/bitcaster/actions/workflows/security.yml/badge.svg)](https://github.com/bitcaster-io/bitcaster/actions/workflows/security.yml)
[![GitHub Code Scanning](https://img.shields.io/github/search/bitcaster-io/bitcaster/label%3Asecurity-event?label=security%20issues)](https://github.com/bitcaster-io/bitcaster/security)
[![codecov](https://codecov.io/gh/bitcaster-io/bitcaster/graph/badge.svg?token=kAuZEX5k5o)](https://codecov.io/gh/bitcaster-io/bitcaster)
[![License](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fbitcaster-io%2Fbitcaster%2Fdevelop%2Fpyproject.toml&query=project.license.text&label=license)](https://github.com/bitcaster-io/bitcaster?tab=License-1-ov-file)
[![Docker](https://img.shields.io/docker/pulls/os4d/bitcaster)](https://hub.docker.com/r/os4d/bitcaster/tags)


Bitcaster is a system-to-user signal-to-message notification system.

Bitcaster will receive signals from any of your applications/systems using a simple RESTful API and will convert them in messages to be distributed to you users via a plethora of channels.

Messages content is customised at user/receiver level using a flexible template system.

Your user will be empowered with an easy to use console to choose how to receive the messages configured in Bitcaster.



[codecov-badge]: https://codecov.io/gh/os4d:bitcaster/bitcaster/branch/develop/graph/badge.svg
[codecov-link]: https://app.codecov.io/gl/os4d:bitcaster/bitcaster


# Resources

- [Home](https://www.bitcaster.io/)
- [Documentation](https://bitcaster-io.github.io/bitcaster/)
- [Bug Tracker](https://github.com/bitcaster-io/bitcaster/issues)
- [Code](https://github.com/bitcaster-io/bitcaster/)
- [Transifex](https://explore.transifex.com/bitcaster/bitcaster/) (Translate Bitcaster\!)

## Code Quality & Security

The project uses several tools to ensure code quality and security:

- [Django](https://www.djangoproject.com/) for the web framework
- [Semgrep](https://semgrep.dev/) for static analysis and security scanning
- [Pytest](https://docs.pytest.org/en/stable/) for testing
- [ESLint](https://eslint.org/) for JavaScript linting
- [Prettier](https://prettier.io/) for code formatting

### Security Rules

#### Admin List_Display Sensitive Fields Detection
A new Semgrep security rule has been added to detect sensitive fields in Django admin `list_display` configurations. This rule prevents exposure of secrets, keys, passwords, or tokens in the changelist view which poses a significant security risk.

**Fields Detected:**
- `secret`
- `key`
- `password`
- `token`
- `api_key`
- `client_secret`
- `private_key`
- `access_token`
- `refresh_token`
- `auth_token`
- `secret_key`

**Why This Matters:**
Exposing sensitive information like API keys, passwords, or tokens in admin changelist views allows unauthorized users to gain access to critical system resources. Even users with limited permissions might be able to see these values if they are displayed in the list view.

**How It Helps Prevent Security Issues:**
This rule automatically detects and flags any instance where sensitive fields appear in `list_display`, preventing accidental exposure of confidential data. It enforces security best practices by requiring developers to explicitly hide or mask sensitive information in Django admin interfaces.
