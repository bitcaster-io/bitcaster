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

**Options**:
- `-p, --processes INTEGER`: Number of worker processes (default: 1).
- `-t, --threads INTEGER`: Number of threads per process (default: 1).
- `-d, --debug`: Enable debug logging.
- `-v, --verbose`: Increase verbosity (use `-vv` for more detail).
- `--reset`: Clear all pending tasks in the queue before starting.
- `--pid-file PATH`: Write the worker PID to this file.
- `--autoreload`: Automatically restart workers when code changes (useful for development).

---

### 2. Task Scheduler (`bc cron`)
Starts the scheduler that triggers periodic tasks, such as monitors, log rotation, and system maintenance. It uses **APScheduler**.

**Usage**:
```bash
bc cron [OPTIONS]
```

**Options**:
- `-d, --debug`: Enable debug logging.
- `-v, --verbose`: Increase verbosity (use `-vv` for more detail; default: 3).
- `--autoreload`: Restart the scheduler on code changes.

> **Note**: For a fully functional Bitcaster instance, both `bc run` and `bc cron` must be running.

---

### 3. Queue Management (`bc queue`)
Tools to inspect and manage the state of the message queues (Redis/RabbitMQ).

**Usage**:
```bash
bc queue [OPTIONS] COMMAND [ARGS]...
```

**Options**:
- `-l, --loglevel TEXT`: Logging level (default: `info`).

**Subcommands**:
- `bc queue list`: Lists all queues content — shows the status of active runners and the number of messages waiting in each queue.
- `bc queue reset`: Safely clears all pending tasks from all queues.

---

### 4. Data Import (`bc import`)
Used for mass-importing data into the system.

**Usage**:
```bash
bc import users [OPTIONS] CSV_FILE
```

**Arguments**:
- `CSV_FILE`: Path to the CSV file to import (required).

**Options**:
- `--org SLUG`: Target organization (defaults to the first local one).
- `--group NAME`: Optional group to add users to.

The import result is printed to the console: `Processed N lines, created/updated M users`. Errors (missing organization or group) are reported per import run.

---

### 5. Diagnostics (`bc inspect`)
Lists all registered background tasks (actors) available in the system. This is useful for verifying that custom dispatchers or plugins are correctly recognized by the worker.

**Usage**:
```bash
bc inspect [OPTIONS]
```

**Options**:
- `-l, --loglevel TEXT`: Logging level (default: `info`).

## Environment Variables

The CLI respects the following environment variables:
- `DJANGO_SETTINGS_MODULE`: Defaults to `bitcaster.config.settings`.
- `BITCASTER_DEBUG`: If set to `true`, enables debug logging.
- `DATABASE_URL`, `REDIS_URL`: Used to connect to infrastructure services.
