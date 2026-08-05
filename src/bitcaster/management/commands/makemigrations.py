import sys
from pathlib import Path

from django.conf import settings
from django.core.management.commands import makemigrations
from django.db.migrations.loader import MigrationLoader

TEMPLATE = """Django migrations lock file. This helps us avoid migration conflicts on master.
If you have a conflict in this file, it means that someone has committed a migration
ahead of you.

To resolve this, rebase against latest master and regenerate your migration. This file
will then be regenerated, and you should be able to merge without conflicts.

{lockfile_content}
"""


def validate(migrations_filepath: Path, latest_migration_by_app: dict[str, str], *, stderr) -> None:
    infile: dict[str, str] = {}

    if not migrations_filepath.exists():
        stderr.write(f"Lockfile does not exist at '{migrations_filepath}', skipping validation.")
        return

    with open(migrations_filepath, encoding="utf-8") as file:
        for line in file:
            if ": " in line:
                app_label, name = line.strip().split(": ", 1)
                infile[app_label] = name

    has_error = False
    for app_label, name in sorted(latest_migration_by_app.items()):
        file_migration = infile.get(app_label)
        if file_migration != name:
            stderr.write(
                f"ERROR: The latest migration does not match the lockfile for `{app_label}` app: "
                f"expected '{name}', found '{file_migration or 'NONE'}'"
            )
            has_error = True

    if has_error:
        sys.exit(2)


def get_latest_migrations() -> dict[str, str]:
    loader = MigrationLoader(None, ignore_no_migrations=True)
    whitelist = getattr(settings, "MIGRATIONS_LOCKFILE_APP_WHITELIST", None)

    latest_migration_by_app: dict[str, str] = {}
    for app_label, name in loader.graph.leaf_nodes():
        if whitelist and app_label not in whitelist:
            continue
        latest_migration_by_app[app_label] = name

    return latest_migration_by_app


class Command(makemigrations.Command):
    def handle(self, *app_labels, **options):
        if not options.get("name") and not options.get("check_changes"):
            self.stderr.write(
                "Please name your migrations using `-n <migration_name>`. For example, `-n backfill_my_new_table`"
            )
            return

        super().handle(*app_labels, **options)

        latest_migration_by_app = get_latest_migrations()

        lockfile_dir = Path(getattr(settings, "MIGRATIONS_LOCKFILE_PATH", settings.PROJECT_ROOT))
        migrations_filepath = lockfile_dir / "migrations_lockfile.txt"

        if options.get("check_changes"):
            validate(migrations_filepath, latest_migration_by_app, stderr=self.stderr)
        else:
            result = "\n".join(f"{app_label}: {name}" for app_label, name in sorted(latest_migration_by_app.items()))

            lockfile_dir.mkdir(parents=True, exist_ok=True)
            migrations_filepath.write_text(
                TEMPLATE.format(lockfile_content=result),
                encoding="utf-8",
            )
