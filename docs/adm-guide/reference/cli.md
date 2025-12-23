# Command-Line Interface (CLI)

Bitcaster provides several command-line tools for administration, setup, and development. These are standard Django management commands and are executed using `manage.py`.

## `upgrade`

This is the most important command for installing and upgrading your Bitcaster instance. It performs all necessary steps to get your system ready.

```bash
./manage.py upgrade [options]
```

**Key Functions:**

-   Runs database migrations.
-   Collects all static files.
-   Creates initial database revisions for auditing.
-   Initializes the core Bitcaster application and permissions.
-   Creates a superuser account if one does not exist.
-   Sets up scheduled tasks for background processing.

**Common Options:**

-   `--admin-email <email>`: Sets the email for the administrator account.
-   `--admin-password <password>`: Sets the password for the administrator account.
-   `--no-migrate`: Skips the database migration step.
-   `--no-static`: Skips the `collectstatic` step.

**Example:**

```bash
./manage.py upgrade --admin-email admin@example.com --admin-password "secure_password"
```

---

## `env`

This command helps you manage and inspect your environment configuration. It's useful for debugging and setting up your `.env` files.

```bash
./manage.py env [options]
```

**Key Functions:**

-   Displays the current environment variables that Bitcaster uses.
-   Checks for missing but required environment variables.
-   Generates configuration files for development or production.

**Common Options:**

-   `--check`: Verifies that all required environment variables are set.
-   `--develop`: Displays development-specific values.
-   `--config`: Shows only the variables that have been explicitly set.
-   `--pattern '{key}="{value}"'`: Formats the output according to the given pattern.

**Example:**

Generate a list of environment variables for a `.env` file:

```bash
./manage.py env --develop --config --pattern='{key}="{value}"' > .env
```

---

## `develop`

This command is designed for setting up a fully-featured local development environment. It populates the database with sample data, making it easier to test and develop new features.

```bash
./manage.py develop [options]
```

**Key Functions:**

-   Loads initial data from a snapshot if available.
-   If no snapshot exists, it creates a sample organization, project, application, and channels.
-   Configures SSO providers (like Google and GitHub) if the corresponding environment variables are set.
-   Can create a data snapshot for later use.

**Common Options:**

-   `--snap`: Creates a data snapshot of the current database state into a file named `.initial_data.json`.

**Example:**

Set up the development environment with sample data:

```bash
./manage.py develop
```
