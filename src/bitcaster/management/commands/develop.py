from typing import TYPE_CHECKING, Any

import logging
import os
import sys
from pathlib import Path

from concurrency.api import disable_concurrency
from flags.state import enable_flag

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management import BaseCommand, call_command
from django.core.management.base import CommandError, SystemCheckError
from strategy_field.utils import fqn

from bitcaster.auth.constants import Grant
from bitcaster.dispatchers import (
    GMailDispatcher,
    LocalDatabaseDispatcher,
    MailJetDispatcher,
    MailgunDispatcher,
    SlackDispatcher,
)
from bitcaster.models import UserRole

if TYPE_CHECKING:
    from argparse import ArgumentParser

    from bitcaster.models import Project, User

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
        sys.path.insert(0, str(settings.SOURCE_DIR.parent / "tests/extras"))
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
        from bitcaster.models import Application, Channel, Organization, User
        from bitcaster.social.models import SocialProvider

        try:
            self.echo("Configuring development environment", style_func=self.style.WARNING)
            bitcaster = Application.objects.get(name__iexact="bitcaster")

            if os.environ.get("GOOGLE_CLIENT_ID") and os.environ.get("GOOGLE_CLIENT_SECRET"):
                sso, __ = SocialProvider.objects.update_or_create(
                    provider="google",
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
                    provider="github",
                    defaults={
                        "configuration": {
                            "SOCIAL_AUTH_GITHUB_KEY": os.environ.get("GITHUB_KEY"),
                            "SOCIAL_AUTH_GITHUB_SECRET": os.environ.get("GITHUB_SECRET"),
                        }
                    },
                )
                self.echo(f"Created/Updated SSO {sso}", style_func=self.style.SUCCESS)

            user: "User | None" = None
            project: "Project | None" = None
            if structure := os.environ.get("TEST_ORG_STRUCTURE", "user@example.com;Org;Project1;Application1"):
                envs = ["develop", "staging", "production"]
                email, org_name, prj_name, apps = structure.split(";")
                u = User.objects.update_or_create(username=email, defaults={"email": email, "is_staff": True})[0]
                u.set_password("password")
                o = u.managed_organizations.filter(name=org_name).first()
                if o is None:
                    o = Organization.objects.local().first()
                if o is None:
                    o = Organization.objects.create(name=org_name, owner=u)
                else:
                    o.owner = u
                    o.save()
                p = o.projects.update_or_create(name=prj_name, owner=u, defaults={"environments": envs})[0]
                active_project = p
                user = u
                project = p
                from bitcaster.constants import bitcaster

                UserRole.objects.get_or_create(user=u, organization=o, group=bitcaster.get_default_group())

                self.echo(f"Created/Updated Organization {org_name}", style_func=self.style.SUCCESS)
                self.echo(f"Created/Updated Project {prj_name}", style_func=self.style.SUCCESS)
                for app_name in apps.split(","):
                    if app_name.strip():
                        a = p.applications.update_or_create(name=app_name, owner=u)[0]
                        a.events.update_or_create(name="Test Event")
                        k = os.environ.get("TEST_API_KEY", "dev-key-trigger-01")
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

            if user and project:
                self.setup_quickstart(user, project)

            enable_flag("DEVELOP_DEBUG_TOOLBAR")
            sys.path.append("/Users/sax/Documents/data/PROGETTI/os4d/bitcaster/tests/extras")
            from testutils.factories import AddressFactory

            AddressFactory.create_batch(10)

            self.echo("System configured", style_func=self.style.SUCCESS)

            self._display_trigger_instructions()
        except ValidationError as e:
            self.halt(Exception("\n- ".join(["Wrong argument(s):", *e.messages])))
        except (CommandError, SystemCheckError) as e:
            self.halt(e)
        except Exception as e:
            self.stdout.write(str(e), style_func=self.style.ERROR)
            logger.exception(e)
            self.halt(e)

    def setup_quickstart(self, user: "User", project: "Project") -> None:
        from bitcaster.constants import AddressType
        from bitcaster.models import Address, Assignment, Channel, Notification, Subscription
        from bitcaster.models.choices import FILTERING_SUBSCRIPTION

        channel = Channel.objects.filter(project=project).first()
        if channel is None:
            channel, __ = Channel.objects.update_or_create(
                name="Test",
                project=project,
                defaults={"dispatcher": fqn(LocalDatabaseDispatcher), "config": {}},
            )
            self.echo(f"Created/Updated Channel {channel}", style_func=self.style.SUCCESS)

        address, __ = Address.objects.get_or_create(
            user=user, value=user.email or user.username, defaults={"name": "Primary", "type": AddressType.EMAIL}
        )
        assignment, __ = Assignment.objects.update_or_create(
            address=address,
            channel=channel,
            defaults={"validated": True, "active": True},
        )
        self.echo(f"Created/Updated Assignment {assignment}", style_func=self.style.SUCCESS)

        for app in project.applications.all():
            for event in app.events.all():
                event.channels.add(channel)
                notification, __ = Notification.objects.update_or_create(
                    event=event,
                    name="Default",
                    defaults={
                        "description": "Notification created by the develop command (Quick Start)",
                        "policy": FILTERING_SUBSCRIPTION,
                        "active": True,
                    },
                )
                notification.create_message(
                    "Default",
                    channel,
                    defaults={
                        "subject": "[Bitcaster] {{ event.name }}",
                        "content": "Hello {{ user.first_name }}, event {{ event.name }} was triggered",
                    },
                )
                Subscription.objects.update_or_create(
                    notification=notification, assignment=assignment, defaults={"active": True}
                )
                self.echo(f"Created/Updated Subscription {assignment} -> {notification}", style_func=self.style.SUCCESS)

    def _display_trigger_instructions(self) -> None:  # pragma: no cover
        from bitcaster.models import Event

        self.echo("\nTrigger your first event:", style_func=self.style.SUCCESS)

        try:
            evt: Event = Event.objects.select_related("application__project__organization").first()
            if not evt:
                self.echo("  No events found.", style_func=self.style.WARNING)
                return

            org_slug = evt.application.project.organization.slug
            prj_slug = evt.application.project.slug
            app_slug = evt.application.slug
            event_slug = evt.slug

            api_key = evt.application.apikey_set.filter(grants__contains=["EVENT_TRIGGER"]).first()
            api_key = str(api_key.key) if api_key else None

            server_url = "http://localhost:8000"
            trigger_url = f"{server_url}/api/o/{org_slug}/p/{prj_slug}/a/{app_slug}/e/{event_slug}/trigger/"

            self.echo(
                f"\nTrigger URL: {trigger_url}",
            )

            if api_key:
                self.echo("\n\n# --- curl ---", style_func=self.style.NOTICE)
                self.echo(
                    f"curl -X POST {trigger_url} \\\n"
                    f"    -H 'Authorization: Key {api_key}' \\\n"
                    f"    -H 'Content-Type: application/json' \\\n"
                    f'    -d \'{{"context": {{"hello": "world"}}}}\''
                )

                self.echo("\n\n# --- bitcaster-sdk (Python) ---", style_func=self.style.NOTICE)
                self.echo(
                    f"pip install bitcaster-sdk\n"
                    f"export BITCASTER_BAE=http://{api_key}@localhost:8000/api/o/{org_slug}/\n"
                    f"import bitcaster_sdk\n"
                    f"bitcaster_sdk.init()\n"
                    f"from bitcaster_sdk import trigger\n"
                    f"trigger('{prj_slug}', '{app_slug}', '{event_slug}', context={{'hello': 'world'}})\n"
                )

                self.echo("\n\n# --- bitcaster-sdk (CLI) ---", style_func=self.style.NOTICE)
                self.echo(
                    f"export BITCASTER_BAE=http://{api_key}@localhost:8000/api/o/{org_slug}/\n"
                    f"bitcaster trigger {prj_slug} {app_slug} {event_slug}"
                )
        except Exception:
            self.echo("  Could not load trigger info.", style_func=self.style.WARNING)
