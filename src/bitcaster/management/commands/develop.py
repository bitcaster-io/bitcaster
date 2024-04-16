import logging
import os
import sys
from typing import TYPE_CHECKING, Any

from django.core.exceptions import ValidationError
from django.core.management import BaseCommand
from django.core.management.base import CommandError, SystemCheckError
from strategy_field.utils import fqn

from bitcaster.config import env
from bitcaster.dispatchers import GMmailDispatcher
from bitcaster.models import Channel

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

    def halt(self, e: Exception) -> None:  # pragma: no cover
        self.stdout.write(str(e), style_func=self.style.ERROR)
        self.stdout.write("\n\n***", style_func=self.style.ERROR)
        self.stdout.write("SYSTEM HALTED", style_func=self.style.ERROR)
        self.stdout.write("Unable to start...", style_func=self.style.ERROR)
        if self.debug:
            raise e

        sys.exit(1)

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: C901
        from bitcaster.models import Application
        from bitcaster.social.models import Provider, SocialProvider

        self.get_options(options)
        if self.verbosity >= 1:
            echo = self.stdout.write
        else:
            echo = lambda *a, **kw: None  # noqa: E731

        try:
            echo("Configuring development environment", style_func=self.style.WARNING)
            bitcaster = Application.objects.get(name="bitcaster")

            if GOOGLE_CLIENT_ID := os.environ.get("GOOGLE_CLIENT_ID") and (
                GOOGLE_CLIENT_SECRET := os.environ.get("GOOGLE_CLIENT_SECRET")
            ):
                sso, __ = SocialProvider.objects.get_or_create(
                    provider=Provider.GOOGLE_OAUTH2,
                    defaults={
                        "configuration": {
                            "SOCIAL_AUTH_GOOGLE_OAUTH2_KEY": GOOGLE_CLIENT_ID,
                            "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET": GOOGLE_CLIENT_SECRET,
                        }
                    },
                )
                echo(f"Created/Updated SSO {sso}", style_func=self.style.SUCCESS)
            if GMAIL_USER := os.environ.get("GMAIL_USER") and (GMAIL_PASSWORD := os.environ.get("GMAIL_PASSWORD")):
                ch, __ = Channel.objects.get_or_create(
                    name="Gmail",
                    defaults={
                        "application": bitcaster,
                        "dispatcher": fqn(GMmailDispatcher),
                        "config": {"username": GMAIL_USER, "password": GMAIL_PASSWORD},
                    },
                )
                echo(f"Created/Updated Channel {ch}", style_func=self.style.SUCCESS)
            if MAILGUN_SENDER_DOMAIN := os.environ.get("MAILGUN_SENDER_DOMAIN") and (
                MAILGUN_API_KEY := os.environ.get("MAILGUN_API_KEY")
            ):
                ch, __ = Channel.objects.get_or_create(
                    name="Mailgun",
                    defaults={
                        "application": bitcaster,
                        "dispatcher": fqn(GMmailDispatcher),
                        "config": {"api_key": MAILGUN_API_KEY, "sender_domain": MAILGUN_SENDER_DOMAIN},
                    },
                )
                echo(f"Created/Updated Channel {ch}", style_func=self.style.SUCCESS)
            if MAILJET_API_KEY := os.environ.get("MAILJET_API_KEY") and (
                MAILJET_SECRET_KEY := os.environ.get("MAILJET_SECRET_KEY")
            ):
                ch, __ = Channel.objects.get_or_create(
                    name="MailJet",
                    defaults={
                        "application": bitcaster,
                        "dispatcher": fqn(GMmailDispatcher),
                        "config": {"api_key": MAILJET_API_KEY, "secret_key": MAILJET_SECRET_KEY},
                    },
                )
                echo(f"Created/Updated Channel {ch}", style_func=self.style.SUCCESS)

            echo("System configured", style_func=self.style.SUCCESS)
        except ValidationError as e:
            self.halt(Exception("\n- ".join(["Wrong argument(s):", *e.messages])))
        except (CommandError, SystemCheckError) as e:
            self.halt(e)
        except Exception as e:
            raise
            self.stdout.write(str(e), style_func=self.style.ERROR)
            logger.exception(e)
            self.halt(e)
