# Command Line Interface (bc)

The `bc` command is the primary entry point for managing Bitcaster's background infrastructure and performing administrative tasks from the terminal.

It is built on top of the **Click** library and automatically initializes the Django environment before executing any command.

---

## Global Options

- `--version`: Show the version and exit.
- `--debug`: Enable debug mode (can also be set via `BITCASTER_DEBUG` environment variable).
- `--help`: Show help message for any command or subcommand.

---

## Main Commands

### 1. Worker Management (`bc run`)
Starts the background workers responsible for physically sending messages and processing tasks. Bitcaster uses **Dramatiq** as its task runner.

**Usage**:
```bash
bc run [OPTIONS]
```

**Common Options**:
- `-p, --processes INTEGER`: Number of worker processes (default: 1).
- `-t, --threads INTEGER`: Number of threads per process (default: 1).
- `--autoreload`: Automatically restart workers when code changes (useful for development).
- `--reset`: Clear all pending tasks in the queue before starting.

---

### 2. Task Scheduler (`bc cron`)
Starts the scheduler that triggers periodic tasks, such as monitors, log rotation, and system maintenance. It uses **APScheduler**.

**Usage**:
```bash
bc cron [OPTIONS]
```

**Common Options**:
- `-v, --verbose`: Increase output verbosity.
- `--autoreload`: Restart the scheduler on code changes.

> **Note**: For a fully functional Bitcaster instance, both `bc run` and `bc cron` must be running.

---

### 3. Queue Management (`bc queue`)
Tools to inspect and manage the state of the message queues (Redis/RabbitMQ).

**Subcommands**:
- `bc queue list`: Shows the number of messages waiting in each queue and the status of active runners.
- `bc queue reset`: Safely clears all pending tasks from all queues.

---

### 4. Data Import (`bc import`)
Used for mass-importing data into the system.

**Subcommands**:
- `bc import users`: Import users from a CSV file.
    - `--org SLUG`: Target organization (defaults to the first local one).
    - `--group NAME`: Optional group to add users to.

---

### 5. Diagnostics (`bc inspect`)
Lists all registered background tasks (actors) available in the system. This is useful for verifying that custom dispatchers or plugins are correctly recognized by the worker.

---

## Environment Variables

The CLI respects the following environment variables:
- `DJANGO_SETTINGS_MODULE`: Defaults to `bitcaster.config.settings`.
- `BITCASTER_DEBUG`: If set to `true`, enables debug logging.
- `DATABASE_URL`, `REDIS_URL`: Used to connect to infrastructure services.
