import logging
import os
import sys
from typing import TYPE_CHECKING, Any

from django.core.exceptions import ValidationError
from django.core.management import BaseCommand
from django.core.management.base import CommandError, SystemCheckError
from flags.state import enable_flag
from strategy_field.utils import fqn

from bitcaster.auth.constants import Grant
from bitcaster.dispatchers import (
    GMailDispatcher,
    MailgunDispatcher,
    MailJetDispatcher,
    SlackDispatcher,
)

if TYPE_CHECKING:
    from argparse import ArgumentParser

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    requires_migrations_checks = False
    requires_system_checks = []

    def add_arguments(self, parser: "ArgumentParser") -> None:
        # parser.add_argument(
        #     "--with-check",
        #     action="store_true",
        #     dest="check",
        #     default=False,
        #     help="Run checks",
        # )
        # parser.add_argument(
        #     "--no-check",
        #     action="store_false",
        #     dest="check",
        #     default=False,
        #     help="Do not run checks",
        # )
        # parser.add_argument(
        #     "--no-migrate",
        #     action="store_false",
        #     dest="migrate",
        #     default=True,
        #     help="Do not run migrations",
        # )
        # parser.add_argument(
        #     "--prompt",
        #     action="store_true",
        #     dest="prompt",
        #     default=False,
        #     help="Let ask for confirmation",
        # )
        parser.add_argument(
            "--debug",
            action="store_true",
            dest="debug",
            default=False,
            help="debug mode",
        )

    # parser.add_argument(
    #     "--no-static",
    #     action="store_false",
    #     dest="static",
    #     default=True,
    #     help="Do not run collectstatic",
    # )
    #
    # parser.add_argument(
    #     "--admin-email",
    #     action="store",
    #     dest="admin_email",
    #     default="",
    #     help="Admin email",
    # )
    # parser.add_argument(
    #     "--admin-password",
    #     action="store",
    #     dest="admin_password",
    #     default="",
    #     help="Admin password",
    # )

    def get_options(self, options: dict[str, Any]) -> None:
        self.verbosity = options["verbosity"]

        #     self.run_check = options["check"]
        #     self.prompt = not options["prompt"]
        #     self.static = options["static"]
        #     self.migrate = options["migrate"]
        self.debug = options["debug"]

    #
    #     self.admin_email = str(options["admin_email"] or env("ADMIN_EMAIL", ""))
    #     self.admin_password = str(options["admin_password"] or env("ADMIN_PASSWORD", ""))

    def halt(self, e: Exception) -> None:  # pragma: no cover
        self.stdout.write(str(e), style_func=self.style.ERROR)
        self.stdout.write("\n\n***", style_func=self.style.ERROR)
        self.stdout.write("SYSTEM HALTED", style_func=self.style.ERROR)
        self.stdout.write("Unable to start...", style_func=self.style.ERROR)
        if self.debug:
            raise e

        sys.exit(1)

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: C901
        from bitcaster.models import Application, Channel, User
        from bitcaster.social.models import Provider, SocialProvider

        self.get_options(options)
        if self.verbosity >= 1:
            echo = self.stdout.write
        else:
            echo = lambda *a, **kw: None  # noqa: E731

        try:
            echo("Configuring development environment", style_func=self.style.WARNING)
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
                echo(f"Created/Updated SSO {sso}", style_func=self.style.SUCCESS)
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
                echo(f"Created/Updated SSO {sso}", style_func=self.style.SUCCESS)

            if structure := os.environ.get("TEST_ORG_STRUCTURE", "user@example.com;Org;Project1;Application1"):
                email, org_name, prj_name, app_name = structure.split(";")
                u = User.objects.update_or_create(username=email, defaults={"email": email, "is_staff": True})[0]
                u.set_password("password")
                o = u.organizations.update_or_create(name=org_name)[0]
                p = o.projects.update_or_create(name=prj_name, owner=u)[0]
                a = p.applications.update_or_create(name=app_name, owner=u)[0]
                ch = o.channel_set.update_or_create(dispatcher=fqn(GMailDispatcher))[0]
                e = a.events.update_or_create(name="Test Event")[0]
                e.channels.add(ch)

                if k := os.environ.get("TEST_API_KEY"):
                    u.keys.update_or_create(
                        name="Key1", defaults={"key": k, "application": a, "grants": [Grant.EVENT_TRIGGER]}
                    )

                echo(f"Created/Updated Organization {org_name}", style_func=self.style.SUCCESS)
                echo(f"Created/Updated Project {prj_name}", style_func=self.style.SUCCESS)
                echo(f"Created/Updated Application {app_name}", style_func=self.style.SUCCESS)

            if os.environ.get("GMAIL_USER") and os.environ.get("GMAIL_PASSWORD"):
                ch, __ = Channel.objects.update_or_create(
                    name="Gmail",
                    defaults={
                        "application": bitcaster,
                        "dispatcher": fqn(GMailDispatcher),
                        "config": {
                            "username": os.environ.get("GMAIL_USER"),
                            "password": os.environ.get("GMAIL_PASSWORD"),
                        },
                    },
                )
                echo(f"Created/Updated Channel {ch}", style_func=self.style.SUCCESS)
            if os.environ.get("MAILGUN_SENDER_DOMAIN") and os.environ.get("MAILGUN_API_KEY"):
                ch, __ = Channel.objects.update_or_create(
                    name="Mailgun",
                    defaults={
                        "application": bitcaster,
                        "dispatcher": fqn(MailgunDispatcher),
                        "config": {
                            "api_key": os.environ.get("MAILGUN_API_KEY"),
                            "sender_domain": os.environ.get("MAILGUN_SENDER_DOMAIN"),
                        },
                    },
                )
                echo(f"Created/Updated Channel {ch}", style_func=self.style.SUCCESS)
            if os.environ.get("MAILJET_API_KEY") and os.environ.get("MAILJET_SECRET_KEY"):
                ch, __ = Channel.objects.update_or_create(
                    name="MailJet",
                    defaults={
                        "application": bitcaster,
                        "dispatcher": fqn(MailJetDispatcher),
                        "config": {
                            "api_key": os.environ.get("MAILJET_API_KEY"),
                            "secret_key": os.environ.get("MAILJET_SECRET_KEY"),
                        },
                    },
                )
                echo(f"Created/Updated Channel {ch}", style_func=self.style.SUCCESS)

            if os.environ.get("SLACK_WEBHOOK"):
                ch, __ = Channel.objects.update_or_create(
                    name="Slack",
                    defaults={
                        "application": bitcaster,
                        "dispatcher": fqn(SlackDispatcher),
                        "config": {"url": os.environ.get("SLACK_WEBHOOK")},
                    },
                )
                echo(f"Created/Updated Channel {ch}", style_func=self.style.SUCCESS)

            enable_flag("DEVELOP_DEBUG_TOOLBAR")

            echo("System configured", style_func=self.style.SUCCESS)
        except ValidationError as e:
            self.halt(Exception("\n- ".join(["Wrong argument(s):", *e.messages])))
        except (CommandError, SystemCheckError) as e:
            self.halt(e)
        except Exception as e:
            self.stdout.write(str(e), style_func=self.style.ERROR)
            logger.exception(e)
            self.halt(e)
