import os
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, List

import pytest
import responses

if TYPE_CHECKING:
    from bitcaster.models import Application, Event, Occurrence, Project, User

here = Path(__file__).parent
sys.path.insert(0, str(here / "../src"))
sys.path.insert(0, str(here / "extras"))


def pytest_addoption(parser) -> None:
    parser.addoption(
        "--with-selenium",
        action="store_true",
        dest="enable_selenium",
        default=False,
        help="enable selenium tests",
    )

    parser.addoption(
        "--show-browser",
        "-S",
        action="store_true",
        dest="show_browser",
        default=False,
        help="will not start browsers in headless mode",
    )

    parser.addoption(
        "--with-sentry",
        action="store_true",
        dest="with_sentry",
        default=False,
        help="enable sentry error logging",
    )

    parser.addoption(
        "--sentry-environment",
        action="store",
        dest="sentry_environment",
        default="test",
        help="set sentry environment",
    )


def pytest_configure(config):
    os.environ.update(DJANGO_SETTINGS_MODULE="bitcaster.config.settings")
    os.environ.setdefault("MEDIA_ROOT", "/tmp/static/")
    os.environ.setdefault("STATIC_ROOT", "/tmp/media/")
    os.environ.setdefault("TEST_EMAIL_SENDER", "sender@example.com")
    os.environ.setdefault("TEST_EMAIL_RECIPIENT", "recipient@example.com")

    os.environ["BITCASTER_LOGGING_LEVEL"] = "CRITICAL"
    os.environ["REDIS_LOGGING_LEVEL"] = "CRITICAL"
    os.environ["DJANGO_LOGGING_LEVEL"] = "CRITICAL"
    os.environ["CELERY_TASK_ALWAYS_EAGER"] = "True"

    os.environ["CSRF_COOKIE_SECURE"] = "False"
    os.environ["CSRF_TRUSTED_ORIGINS"] = "https://close-pro-impala.ngrok-free.app,http://localhost"

    os.environ["LOGGING_LEVEL"] = "CRITICAL"

    os.environ["MAILGUN_API_KEY"] = "11"
    os.environ["MAILGUN_SENDER_DOMAIN"] = "mailgun.domain"
    os.environ["MAILJET_API_KEY"] = "11"
    os.environ["MAILJET_SECRET_KEY"] = "11"

    os.environ["SECRET_KEY"] = "super-secret-key-just-for-testing"
    os.environ["SECURE_HSTS_PRELOAD"] = "0"
    os.environ["SECURE_SSL_REDIRECT"] = "False"
    os.environ["SESSION_COOKIE_DOMAIN"] = ""
    os.environ["SESSION_COOKIE_SECURE"] = "False"
    os.environ["SOCIAL_AUTH_REDIRECT_IS_HTTPS"] = "False"

    os.environ["STORAGE_DEFAULT"] = "django.core.files.storage.FileSystemStorage"
    os.environ["STORAGE_MEDIA"] = "django.core.files.storage.FileSystemStorage"
    os.environ["STORAGE_STTIC"] = "django.core.files.storage.FileSystemStorage"

    os.environ["GMAIL_USER"] = "user@example.com"
    os.environ["GMAIL_PASSWORD"] = "11"

    os.environ["TWILIO_SID"] = "abc"

    if not config.option.with_sentry:
        os.environ["SENTRY_DSN"] = ""
    else:
        os.environ["SENTRY_ENVIRONMENT"] = config.option.sentry_environment

    if not config.option.enable_selenium:
        config.option.enable_selenium = "selenium" in config.option.markexpr

    config.addinivalue_line("markers", "skip_test_if_env(env): this mark skips the tests for the given env")
    from django.conf import settings

    settings.ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
    settings.MEDIA_ROOT = "%s/media" % tempfile.gettempdir()
    settings.STATIC_ROOT = "%s/static" % tempfile.gettempdir()
    settings.MESSAGE_STORAGE = "testutils.messages.PlainCookieStorage"

    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    os.makedirs(settings.STATIC_ROOT, exist_ok=True)

    import django
    from django.core.management import CommandError, call_command

    django.setup()
    from testutils.dispatcher import XDispatcher

    from bitcaster.dispatchers.base import dispatcherManager

    dispatcherManager.register(XDispatcher)

    try:
        call_command("env", check=True)
    except CommandError:
        pytest.exit("FATAL: Environment variables missing")


@pytest.fixture()
def system_objects(admin_user: "User") -> None:
    from django.contrib.auth.models import Group

    from bitcaster.auth.constants import DEFAULT_GROUP_NAME
    from bitcaster.constants import Bitcaster

    Group.objects.get_or_create(name=DEFAULT_GROUP_NAME)
    Bitcaster.initialize(admin_user)


@pytest.fixture(autouse=True)
def clear_state(db):
    from bitcaster.state import state

    try:
        del state.app
    except AttributeError:
        pass


@pytest.fixture()
def mocked_responses():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps


@pytest.fixture
def user(db):
    from testutils.factories.user import UserFactory

    return UserFactory(username="user@example.com", is_active=True)


@pytest.fixture
def system_user(db):
    from testutils.factories.user import UserFactory

    return UserFactory(username="__SYSTEM__")


@pytest.fixture
def superuser(db):
    from testutils.factories.user import SuperUserFactory

    return SuperUserFactory(username="superuser@example.com")


@pytest.fixture()
def os4d(db):
    from testutils.factories.org import OrganizationFactory

    from bitcaster.constants import Bitcaster

    return OrganizationFactory(name=Bitcaster.ORGANIZATION, slug="os4d")


@pytest.fixture()
def bitcaster(os4d) -> "Application":
    from testutils.factories.org import ApplicationFactory

    from bitcaster.constants import Bitcaster

    return ApplicationFactory(
        name=Bitcaster.APPLICATION, project__organization=os4d, project__name=Bitcaster.PROJECT, slug="bitcaster"
    )


@pytest.fixture()
def organization(db):
    from testutils.factories.org import OrganizationFactory

    return OrganizationFactory()


@pytest.fixture()
def project(organization):
    from testutils.factories.org import ProjectFactory

    return ProjectFactory(organization=organization)


@pytest.fixture()
def application(project: "Project"):
    from testutils.factories.org import ApplicationFactory

    return ApplicationFactory(project=project)


@pytest.fixture()
def distributionlist(project: "Project"):
    from testutils.factories.distribution import DistributionListFactory

    return DistributionListFactory(project=project)


@pytest.fixture()
def event(application) -> "Event":
    from testutils.factories import ChannelFactory, EventFactory

    return EventFactory(application=application, channels=[ChannelFactory()], active=True)


@pytest.fixture()
def address(db):
    from testutils.factories.address import AddressFactory

    return AddressFactory()


@pytest.fixture()
def message(db):
    from testutils.factories.message import MessageFactory

    return MessageFactory()


@pytest.fixture()
def channel(project: "Project"):
    from testutils.factories.channel import ChannelFactory

    return ChannelFactory(project=project, organization=project.organization)


@pytest.fixture()
def org_channel(organization):
    from testutils.factories.channel import ChannelFactory

    return ChannelFactory(organization=organization, project=None)


@pytest.fixture()
def email_channel(db):
    from strategy_field.utils import fqn
    from testutils.factories.channel import ChannelFactory

    from bitcaster.dispatchers import GMailDispatcher

    return ChannelFactory(dispatcher=fqn(GMailDispatcher))


@pytest.fixture()
def sms_channel(db):
    from strategy_field.utils import fqn
    from testutils.factories.channel import ChannelFactory

    from bitcaster.dispatchers import TwilioSMS

    return ChannelFactory(dispatcher=fqn(TwilioSMS))


@pytest.fixture()
def api_key(db):
    from testutils.factories.key import ApiKeyFactory

    return ApiKeyFactory()


@pytest.fixture()
def occurrence(db):
    from testutils.factories import OccurrenceFactory

    return OccurrenceFactory()


@pytest.fixture
def purgeable_occurrences(db) -> List["Occurrence"]:
    from datetime import timedelta

    from constance import config
    from django.utils import timezone
    from freezegun import freeze_time
    from testutils.factories import OccurrenceFactory

    with freeze_time(timezone.now() - timedelta(days=config.OCCURRENCE_DEFAULT_RETENTION + 1)):
        occurrence_default_retention = OccurrenceFactory()

    with freeze_time(timezone.now() - timedelta(days=6)):
        occurrence_custom_retention = OccurrenceFactory(event__occurrence_retention=5)

    return [occurrence_default_retention, occurrence_custom_retention]


@pytest.fixture
def non_purgeable_occurrences(db) -> List["Occurrence"]:
    from datetime import timedelta

    from django.utils import timezone
    from freezegun import freeze_time
    from testutils.factories import OccurrenceFactory

    with freeze_time(timezone.now() - timedelta(days=1)):
        non_purgeable_occurrence = OccurrenceFactory(event__occurrence_retention=5)

    return [non_purgeable_occurrence]


@pytest.fixture()
def notification(db):
    from testutils.factories import NotificationFactory

    return NotificationFactory()


@pytest.fixture()
def assignment(db):
    from testutils.factories import AssignmentFactory

    return AssignmentFactory()


@pytest.fixture()
def messagebox() -> list:
    import testutils.dispatcher

    testutils.dispatcher.MESSAGES = []
    yield testutils.dispatcher.MESSAGES
    testutils.dispatcher.MESSAGES = []


@pytest.fixture()
def monitor() -> list:
    from testutils.factories import MonitorFactory

    return MonitorFactory()
