from typing import TYPE_CHECKING, List

import contextlib
import os
import sys
import tempfile
from datetime import timedelta
from pathlib import Path
from uuid import uuid4

import psycopg2
import responses
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import pytest

if TYPE_CHECKING:
    from bitcaster.models import (
        Application,
        Attachment,
        Event,
        Group,
        MessageTemplate,
        Monitor,
        Occurrence,
        ProcessLogEntry,
        Project,
        Task,
        User,
    )

here = Path(__file__).parent
sys.path.insert(0, str(here / "../src"))
sys.path.insert(0, str(here / "extras"))


def pytest_addoption(parser) -> None:
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

    parser.addoption(
        "--test-docker",
        action="store_true",
        dest="test_docker",
        default=False,
        help="run only docker container integration tests",
    )


def pytest_configure(config):
    os.environ.update(DJANGO_SETTINGS_MODULE="bitcaster.config.settings")
    os.environ.setdefault("MEDIA_ROOT", "/tmp/static/")
    os.environ.setdefault("STATIC_ROOT", "/tmp/media/")

    if config.option.test_docker:
        config.option.cov_fail_under = 0
        cov = config.pluginmanager.get_plugin("_cov")
        if cov is not None:
            cov.fail_under = 0
    os.environ.setdefault("TEST_EMAIL_SENDER", "sender@example.com")
    os.environ.setdefault("TEST_EMAIL_RECIPIENT", "recipient@example.com")

    os.environ["BITCASTER_LOGGING_LEVEL"] = "CRITICAL"
    os.environ["REDIS_LOGGING_LEVEL"] = "CRITICAL"
    os.environ["DJANGO_LOGGING_LEVEL"] = "CRITICAL"

    os.environ["CSRF_COOKIE_SECURE"] = "False"
    os.environ["CSRF_TRUSTED_ORIGINS"] = "https://close-pro-impala.ngrok-free.app,http://localhost"

    for entry in os.environ:
        if entry.startswith("LOGGING_"):
            del os.environ[entry]
    os.environ["LOGGING_LEVEL"] = "CRITICAL"
    os.environ["LOGGING_LEVEL_BITCASTER"] = "CRITICAL"

    os.environ["MAILGUN_API_KEY"] = "11"
    os.environ["MAILGUN_SENDER_DOMAIN"] = "mailgun.domain"

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

    config.addinivalue_line("markers", "skip_test_if_env(env): this mark skips the tests for the given env")
    config.addinivalue_line("markers", "docker: docker container integration tests (use --test-docker)")
    from django.conf import settings

    settings.ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
    settings.MEDIA_ROOT = "%s/media" % tempfile.gettempdir()
    settings.STATIC_ROOT = "%s/static" % tempfile.gettempdir()
    settings.MESSAGE_STORAGE = "testutils.messages.PlainCookieStorage"
    settings.SUPERUSERS = ["superuser001@example.com", "superuser002@example.com"]
    settings.CACHE_PREFIX = uuid4().hex

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


def pytest_collection_modifyitems(config, items):
    if config.option.test_docker:
        items[:] = [item for item in items if item.get_closest_marker("docker")]
    else:
        skip = pytest.mark.skip(reason="use --test-docker to enable")
        for item in items:
            if item.get_closest_marker("docker"):
                item.add_marker(skip)


def run_sql(sql):
    conn = psycopg2.connect(database="postgres")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(sql)
    conn.close()


@pytest.fixture
def system_objects(admin_user: "User") -> None:
    from django.contrib.auth.models import Group

    from bitcaster.auth.constants import DEFAULT_GROUP_NAME
    from bitcaster.constants import bitcaster

    Group.objects.get_or_create(name=DEFAULT_GROUP_NAME)
    bitcaster.initialize(admin_user)


@pytest.fixture(autouse=True)
def clear_state(db):
    from bitcaster.state import state

    with contextlib.suppress(AttributeError):
        del state.app


@pytest.fixture(autouse=True)
def allow_multiple_organizations():
    from bitcaster.models import Organization

    Organization._enforce_org_limit = False
    yield
    Organization._enforce_org_limit = True


@pytest.fixture
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


@pytest.fixture
def os4d(db):
    from testutils.factories.org import OrganizationFactory

    from bitcaster.constants import bitcaster

    return OrganizationFactory(name=bitcaster.ORGANIZATION, slug="os4d")


@pytest.fixture
def bitcaster(os4d) -> "Application":
    from testutils.factories.org import ApplicationFactory

    from bitcaster.constants import bitcaster

    return ApplicationFactory.create(
        name=bitcaster.APPLICATION, project__organization=os4d, project__name=bitcaster.PROJECT, slug="bitcaster"
    )


@pytest.fixture
def organization(db):
    from testutils.factories.org import OrganizationFactory

    return OrganizationFactory()


@pytest.fixture
def local_organization(db):
    from testutils.factories import OrganizationFactory

    from bitcaster.constants import bitcaster

    bitcaster._local_org = None
    return OrganizationFactory.create()


@pytest.fixture
def project(organization):
    from testutils.factories.org import ProjectFactory

    return ProjectFactory(organization=organization)


@pytest.fixture
def application(project: "Project"):
    from testutils.factories.org import ApplicationFactory

    return ApplicationFactory(project=project)


@pytest.fixture
def distributionlist(project: "Project"):
    from testutils.factories.distribution import DistributionListFactory

    return DistributionListFactory(project=project)


@pytest.fixture
def event(application) -> "Event":
    from testutils.factories import ChannelFactory, EventFactory

    return EventFactory(application=application, channels=[ChannelFactory()], active=True)


@pytest.fixture
def address(db):
    from testutils.factories.address import AddressFactory

    return AddressFactory()


@pytest.fixture
def message(db):
    from testutils.factories.message import MessageTemplateFactory

    return MessageTemplateFactory()


@pytest.fixture
def channel(project: "Project"):
    from testutils.factories.channel import ChannelFactory

    return ChannelFactory(project=project, organization=project.organization)


@pytest.fixture
def org_channel(organization):
    from testutils.factories.channel import ChannelFactory

    return ChannelFactory(organization=organization, project=None)


@pytest.fixture
def email_channel(db):
    from testutils.factories.channel import ChannelFactory

    from strategy_field.utils import fqn

    from bitcaster.dispatchers import GMailDispatcher

    return ChannelFactory(dispatcher=fqn(GMailDispatcher))


@pytest.fixture
def sms_channel(db):
    from testutils.factories.channel import ChannelFactory

    from strategy_field.utils import fqn

    from bitcaster.dispatchers import TwilioSMS

    return ChannelFactory(dispatcher=fqn(TwilioSMS))


@pytest.fixture
def api_key(db):
    from testutils.factories.key import ApiKeyFactory

    return ApiKeyFactory()


@pytest.fixture
def occurrence(db):
    from testutils.factories import OccurrenceFactory

    return OccurrenceFactory()


@pytest.fixture
def purgeable_occurrences(db) -> List["Occurrence"]:
    from constance import config

    from freezegun import freeze_time
    from testutils.factories import OccurrenceFactory

    from django.utils import timezone

    with freeze_time(timezone.now() - timedelta(days=config.OCCURRENCE_DEFAULT_RETENTION + 1)):
        occurrence_default_retention = OccurrenceFactory.create()

    with freeze_time(timezone.now() - timedelta(days=6)):
        occurrence_custom_retention = OccurrenceFactory.create(event__occurrence_retention=5)

    return [occurrence_default_retention, occurrence_custom_retention]


@pytest.fixture
def non_purgeable_occurrences(db) -> list["Occurrence"]:
    from datetime import timedelta

    from freezegun import freeze_time
    from testutils.factories import OccurrenceFactory

    from django.utils import timezone

    with freeze_time(timezone.now() - timedelta(days=1)):
        non_purgeable_occurrence = OccurrenceFactory.create(event__occurrence_retention=5)

    return [non_purgeable_occurrence]


@pytest.fixture
def notification(db):
    from testutils.factories import NotificationFactory

    return NotificationFactory()


@pytest.fixture
def assignment(db):
    from testutils.factories import AssignmentFactory

    return AssignmentFactory()


@pytest.fixture
def monitor() -> "Monitor":
    from testutils.factories import MonitorFactory

    return MonitorFactory.create()


@pytest.fixture
def message_template() -> "MessageTemplate":
    from testutils.factories import ChannelFactory, EventFactory, MessageTemplateFactory

    from strategy_field.utils import fqn

    from bitcaster.dispatchers import GMailDispatcher

    ch = ChannelFactory.create(dispatcher=fqn(GMailDispatcher))
    event = EventFactory.create(channels=[ch])
    return MessageTemplateFactory.create(event=event, channel=ch)


@pytest.fixture
def group() -> "Group":
    from testutils.factories import GroupFactory

    return GroupFactory.create()


@pytest.fixture
def processlogentry(db) -> "ProcessLogEntry":
    from testutils.factories import ProcessLogEntryFactory

    return ProcessLogEntryFactory.create()


@pytest.fixture
def task() -> "Task":
    from testutils.factories import TaskFactory

    return TaskFactory.create()


@pytest.fixture
def attachment() -> "Attachment":
    from testutils.factories import AttachmentFactory

    return AttachmentFactory.create()
