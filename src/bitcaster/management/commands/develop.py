import logging
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from concurrency.api import disable_concurrency
from django.core.exceptions import ValidationError
from django.core.management import BaseCommand, call_command
from django.core.management.base import CommandError, SystemCheckError
from flags.state import enable_flag
from strategy_field.utils import fqn

from bitcaster.auth.constants import Grant
from bitcaster.dispatchers import (
    GMailDispatcher,
    MailJetDispatcher,
    MailgunDispatcher,
    SlackDispatcher,
)
from bitcaster.models import UserRole

if TYPE_CHECKING:
    from argparse import ArgumentParser

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    requires_migrations_checks = False
    requires_system_checks = []

    def add_arguments(self, parser: "ArgumentParser") -> None:
        parser.add_argument(
            "--debug",
            action="store_true",
            dest="debug",
            default=False,
            help="debug mode",
        )
        parser.add_argument(
            "--snap",
            action="store_true",
            dest="snapshot",
            default=False,
            help="make a data snapshot",
        )

    def get_options(self, options: dict[str, Any]) -> None:
        self.verbosity = options["verbosity"]
        self.debug = options["debug"]
        self.snapshot = options["snapshot"]

    def halt(self, e: Exception) -> None:  # pragma: no cover
        self.stdout.write(str(e), style_func=self.style.ERROR)
        self.stdout.write("\n\n***", style_func=self.style.ERROR)
        self.stdout.write("SYSTEM HALTED", style_func=self.style.ERROR)
        self.stdout.write("Unable to start...", style_func=self.style.ERROR)
        if self.debug:
            raise e

        sys.exit(1)

    @property
    def echo(self):
        if self.verbosity >= 1:
            return self.stdout.write
        return lambda *a, **kw: None  # noqa: E731

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: C901
        self.get_options(options)

        if self.snapshot:
            call_command(
                "dumpdata",
                format="json",
                output=".initial_data.json",
                use_natural_primary_keys=True,
                use_natural_foreign_keys=True,
                use_base_manager=True,
                verbosity=self.verbosity,
            )

        elif Path(".initial_data.json").exists():
            self.echo("Loading initial data...")
            with disable_concurrency():
                call_command("loaddata", ".initial_data.json", verbosity=self.verbosity)
        else:
            self.echo("Creating initial data...")
            self.setup(*args, **options)

    def setup(self, *args: Any, **options: Any) -> None:  # noqa: C901
        from bitcaster.models import Application, Channel, User
        from bitcaster.social.models import Provider, SocialProvider

        try:
            self.echo("Configuring development environment", style_func=self.style.WARNING)
            bitcaster = Application.objects.get(name__iexact="bitcaster")

            if os.environ.get("GOOGLE_CLIENT_ID") and os.environ.get("GOOGLE_CLIENT_SECRET"):
                sso, __ = SocialProvider.objects.update_or_create(
                    provider=Provider.GOOGLE_OAUTH2,
                    defaults={
                        "configuration": {
                            "SOCIAL_AUTH_GOOGLE_OAUTH2_KEY": os.environ.get("GOOGLE_CLIENT_ID"),
                            "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET": os.environ.get("GOOGLE_CLIENT_SECRET"),
                            "SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE": [
                                "https://www.googleapis.com/auth/userinfo.email",
                                "https://www.googleapis.com/auth/userinfo.profile",
                            ],
                        }
                    },
                )
                self.echo(f"Created/Updated SSO {sso}", style_func=self.style.SUCCESS)
            if os.environ.get("GITHUB_KEY") and os.environ.get("GITHUB_SECRET"):
                sso, __ = SocialProvider.objects.update_or_create(
                    provider=Provider.GITHUB,
                    defaults={
                        "configuration": {
                            "SOCIAL_AUTH_GITHUB_KEY": os.environ.get("GITHUB_KEY"),
                            "SOCIAL_AUTH_GITHUB_SECRET": os.environ.get("GITHUB_SECRET"),
                        }
                    },
                )
                self.echo(f"Created/Updated SSO {sso}", style_func=self.style.SUCCESS)

            if structure := os.environ.get("TEST_ORG_STRUCTURE", "user@example.com;Org;Project1;Application1"):
                envs = ["develop", "staging", "production"]
                email, org_name, prj_name, apps = structure.split(";")
                u = User.objects.update_or_create(username=email, defaults={"email": email, "is_staff": True})[0]
                u.set_password("password")
                o = u.managed_organizations.update_or_create(name=org_name)[0]
                p = o.projects.update_or_create(name=prj_name, owner=u, defaults={"environments": envs})[0]
                active_project = p
                from bitcaster.constants import bitcaster

                UserRole.objects.get_or_create(user=u, organization=o, group=bitcaster.get_default_group())

                self.echo(f"Created/Updated Organization {org_name}", style_func=self.style.SUCCESS)
                self.echo(f"Created/Updated Project {prj_name}", style_func=self.style.SUCCESS)
                for app_name in apps.split(","):
                    if app_name.strip():
                        a = p.applications.update_or_create(name=app_name, owner=u)[0]
                        a.events.update_or_create(name="Test Event")
                        if k := os.environ.get("TEST_API_KEY"):
                            u.keys.update_or_create(
                                name="Key1",
                                defaults={
                                    "key": k,
                                    "application": a,
                                    "grants": [Grant.EVENT_TRIGGER, Grant.EVENT_LIST, Grant.SYSTEM_PING],
                                },
                            )
                        self.echo(f"Created/Updated Application {app_name}", style_func=self.style.SUCCESS)
            else:
                active_project = bitcaster
            if os.environ.get("GMAIL_USER") and os.environ.get("GMAIL_PASSWORD"):
                ch, __ = Channel.objects.update_or_create(
                    name="Gmail",
                    project=active_project,
                    defaults={
                        "dispatcher": fqn(GMailDispatcher),
                        "config": {
                            "username": os.environ.get("GMAIL_USER"),
                            "password": os.environ.get("GMAIL_PASSWORD"),
                        },
                    },
                )
                self.echo(f"Created/Updated Channel {ch}", style_func=self.style.SUCCESS)
            self.echo(f"Active Project is {active_project}")
            if os.environ.get("MAILGUN_SENDER_DOMAIN") and os.environ.get("MAILGUN_API_KEY"):
                ch, __ = Channel.objects.update_or_create(
                    name="Mailgun",
                    project=active_project,
                    defaults={
                        "dispatcher": fqn(MailgunDispatcher),
                        "config": {
                            "api_key": os.environ.get("MAILGUN_API_KEY"),
                            "sender_domain": os.environ.get("MAILGUN_SENDER_DOMAIN"),
                        },
                    },
                )
                self.echo(f"Created/Updated Channel {ch}", style_func=self.style.SUCCESS)
            if os.environ.get("MAILJET_API_KEY") and os.environ.get("MAILJET_SECRET_KEY"):
                ch, __ = Channel.objects.update_or_create(
                    name="MailJet",
                    project=active_project,
                    defaults={
                        "dispatcher": fqn(MailJetDispatcher),
                        "config": {
                            "api_key": os.environ.get("MAILJET_API_KEY"),
                            "secret_key": os.environ.get("MAILJET_SECRET_KEY"),
                        },
                    },
                )
                self.echo(f"Created/Updated Channel {ch}", style_func=self.style.SUCCESS)

            if os.environ.get("SLACK_WEBHOOK"):
                ch, __ = Channel.objects.update_or_create(
                    name="Slack",
                    project=active_project,
                    defaults={
                        "dispatcher": fqn(SlackDispatcher),
                        "config": {"url": os.environ.get("SLACK_WEBHOOK")},
                    },
                )
                self.echo(f"Created/Updated Channel {ch}", style_func=self.style.SUCCESS)

            enable_flag("DEVELOP_DEBUG_TOOLBAR")
            sys.path.append("/Users/sax/Documents/data/PROGETTI/os4d/bitcaster/tests/extras")
            from testutils.factories import AddressFactory

            AddressFactory.create_batch(10)

            self.echo("System configured", style_func=self.style.SUCCESS)
        except ValidationError as e:
            self.halt(Exception("\n- ".join(["Wrong argument(s):", *e.messages])))
        except (CommandError, SystemCheckError) as e:
            self.halt(e)
        except Exception as e:
            self.stdout.write(str(e), style_func=self.style.ERROR)
            logger.exception(e)
            self.halt(e)
