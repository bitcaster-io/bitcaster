import logging
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from django.core.exceptions import ValidationError
from django.core.management import BaseCommand, call_command
from django.core.management.base import CommandError, SystemCheckError
from django.core.validators import validate_email
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from flags.state import enable_flag

from bitcaster.config import env
from bitcaster.constants import bitcaster

if TYPE_CHECKING:
    from argparse import ArgumentParser

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    requires_migrations_checks = False
    requires_system_checks = []

    def add_arguments(self, parser: "ArgumentParser") -> None:
        parser.add_argument(
            "--with-check",
            action="store_true",
            dest="check",
            default=False,
            help="Run checks",
        )
        parser.add_argument(
            "--no-check",
            action="store_false",
            dest="check",
            default=False,
            help="Do not run checks",
        )
        parser.add_argument(
            "--no-migrate",
            action="store_false",
            dest="migrate",
            default=True,
            help="Do not run migrations",
        )
        parser.add_argument(
            "--prompt",
            action="store_true",
            dest="prompt",
            default=False,
            help="Let ask for confirmation",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            dest="debug",
            default=False,
            help="debug mode",
        )
        parser.add_argument(
            "--no-static",
            action="store_false",
            dest="static",
            default=True,
            help="Do not run collectstatic",
        )

        parser.add_argument(
            "--admin-email",
            action="store",
            dest="admin_email",
            default="",
            help="Admin email",
        )
        parser.add_argument(
            "--admin-password",
            action="store",
            dest="admin_password",
            default="",
            help="Admin password",
        )

    def get_options(self, options: dict[str, Any]) -> None:
        self.verbosity = options["verbosity"]
        self.run_check = options["check"]
        self.prompt = not options["prompt"]
        self.static = options["static"]
        self.migrate = options["migrate"]
        self.debug = options["debug"]

        self.admin_email = str(options["admin_email"] or env("ADMIN_EMAIL", ""))
        self.admin_password = str(options["admin_password"] or env("ADMIN_PASSWORD", ""))

    def halt(self, e: Exception) -> None:
        self.stdout.write(str(e), style_func=self.style.ERROR)
        self.stdout.write("\n\n***", style_func=self.style.ERROR)
        self.stdout.write("SYSTEM HALTED", style_func=self.style.ERROR)
        self.stdout.write("Unable to start...", style_func=self.style.ERROR)
        if self.debug:
            raise e

        sys.exit(1)

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: C901
        from django.contrib.auth.models import Group

        from bitcaster.models import Organization, Project, User

        self.get_options(options)
        if self.verbosity >= 1:
            echo = self.stdout.write
        else:
            echo = lambda *a, **kw: None  # noqa: E731

        try:
            extra = {
                "no_input": not self.prompt,
                "verbosity": self.verbosity - 1,
                "stdout": self.stdout,
            }
            from django.conf import settings

            echo("Running upgrade", style_func=self.style.WARNING)
            call_command("env", check=True)

            if self.run_check:
                call_command("check", deploy=True, verbosity=self.verbosity - 1)
            if self.static:
                static_root = Path(str(settings.STATIC_ROOT))
                echo(f"Run collectstatic to: '{static_root}' - '{static_root.absolute()}")
                if not static_root.exists():
                    static_root.mkdir(parents=True)
                call_command("collectstatic", **extra)

            if self.migrate:
                echo("Run migrations")
                call_command("migrate", **extra)
                call_command("create_extra_permissions")

            echo("Init reversion")
            call_command("createinitialrevisions")
            call_command("deleterevisions", days=180, keep=3)

            echo("Remove stale contenttypes")
            call_command("remove_stale_contenttypes", **extra)

            admin: User | None
            User.objects.get_or_create(username="__SYSTEM__")
            if self.admin_email:
                if User.objects.filter(email=self.admin_email).exists():
                    echo(
                        f"User {self.admin_email} found, skip creation",
                        style_func=self.style.WARNING,
                    )
                else:
                    enable_flag("LOCAL_LOGIN")
                    echo(f"Creating superuser: {self.admin_email}", style_func=self.style.WARNING)
                    validate_email(self.admin_email)
                    os.environ["DJANGO_SUPERUSER_USERNAME"] = self.admin_email
                    os.environ["DJANGO_SUPERUSER_EMAIL"] = self.admin_email
                    os.environ["DJANGO_SUPERUSER_PASSWORD"] = self.admin_password
                    call_command(
                        "createsuperuser",
                        email=self.admin_email,
                        username=self.admin_email,
                        verbosity=self.verbosity - 1,
                        interactive=False,
                    )

                admin = User.objects.get(email=self.admin_email)
            else:
                admin = User.objects.filter(is_superuser=True).get()

            if not admin:
                raise CommandError("Create an admin user")

            bitcaster.initialize(admin)

            echo(f"Creating address: {self.admin_email}", style_func=self.style.WARNING)
            admin.addresses.get_or_create(name="email", value=self.admin_email)

            from bitcaster.auth.constants import DEFAULT_GROUP_NAME

            Group.objects.get_or_create(name="Admins")
            Group.objects.get_or_create(name=DEFAULT_GROUP_NAME)

            # Inside the function you want to add task dynamically
            schedule_every_minute, _ = CrontabSchedule.objects.get_or_create(minute="*/1")
            PeriodicTask.objects.get_or_create(
                name="occurence_processor",
                defaults={"task": "bitcaster.tasks.schedule_occurrences", "crontab": schedule_every_minute},
            )

            schedule_every_night, _ = CrontabSchedule.objects.get_or_create(hour=3, minute=30)
            PeriodicTask.objects.get_or_create(
                name="purge_occurrences",
                defaults={"task": "bitcaster.tasks.purge_occurrences", "crontab": schedule_every_night},
            )
            if not (org := Organization.objects.local().first()):
                org = Organization.objects.create(name="Organization", owner=admin)

            if not Project.objects.local().exists():
                Project.objects.create(name="Project", owner=admin, organization=org)

            echo("Upgrade completed", style_func=self.style.SUCCESS)
        except ValidationError as e:
            self.halt(Exception("\n- ".join(["Wrong argument(s):", *e.messages])))
        except (CommandError, SystemCheckError) as e:
            self.halt(e)
        except Exception as e:
            self.stdout.write(str(e), style_func=self.style.ERROR)
            logger.exception(e)
            self.halt(e)
