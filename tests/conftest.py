import os
import sys
from pathlib import Path

import django
import pytest
import responses

here = Path(__file__).parent
sys.path.insert(0, str(here / "../src"))
sys.path.insert(0, str(here / "extras"))


def pytest_addoption(parser):
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

    os.environ["MAILGUN_API_KEY"] = "11"
    os.environ["MAILGUN_SENDER_DOMAIN"] = "mailgun.domain"
    os.environ["MAILJET_API_KEY"] = "11"
    os.environ["MAILJET_SECRET_KEY"] = "11"
    os.environ["STORAGE_DEFAULT"] = "django.core.files.storage.FileSystemStorage"
    os.environ["STORAGE_MEDIA"] = "django.core.files.storage.FileSystemStorage"
    os.environ["STORAGE_STTIC"] = "django.core.files.storage.FileSystemStorage"

    os.environ["GMAIL_USER"] = "11"
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
    settings.MEDIA_ROOT = "/tmp/media"
    settings.STATIC_ROOT = "/tmp/static"
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    os.makedirs(settings.STATIC_ROOT, exist_ok=True)

    from django.core.management import CommandError, call_command

    django.setup()
    from testutils.dispatcher import TDispatcher

    from bitcaster.dispatchers.base import dispatcherManager

    dispatcherManager.register(TDispatcher)

    try:
        call_command("env", check=True)
    except CommandError:
        pytest.exit("FATAL: Environment variables missing")


@pytest.fixture(autouse=True)
def defaults(db):
    from django.contrib.auth.models import Group

    from bitcaster.auth.constants import DEFAULT_GROUP_NAME

    Group.objects.get_or_create(name=DEFAULT_GROUP_NAME)


@pytest.fixture(autouse=True)
def clear_state(db):
    from bitcaster.state import state

    try:
        del state.app
    except AttributeError:
        pass


@pytest.fixture()
def system_events(admin_user):
    from bitcaster.constants import Bitcaster

    Bitcaster.initialize(admin_user)


def pytest_runtest_setup(item):
    driver = item.config.getoption("--driver") or ""

    if driver.lower() == "firefox" and list(item.iter_markers(name="skip_if_firefox")):
        pytest.skip("Test skipped because Firefox")
    if driver.lower() == "safari" and list(item.iter_markers(name="skip_if_safari")):
        pytest.skip("Test skipped because Safari")
    if driver.lower() == "edge" and list(item.iter_markers(name="skip_if_edge")):
        pytest.skip("Test skipped because Edge")

    env_names = [mark.args[0] for mark in item.iter_markers(name="skip_test_if_env")]
    if env_names:
        if item.config.getoption("--env") in os.environ:
            pytest.skip(f"Test skipped because env {env_names!r} is present")


def pytest_collection_modifyitems(config, items):
    if not config.option.enable_selenium:
        skip_mymarker = pytest.mark.skip(reason="selenium not enabled")
        for item in items:
            if list(item.iter_markers(name="selenium")):
                item.add_marker(skip_mymarker)


@pytest.fixture()
def mocked_responses():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps


@pytest.fixture
def user(db):

    from testutils.factories.user import UserFactory

    return UserFactory(username="user@example.com", is_active=True)


@pytest.fixture
def superuser(db):

    from testutils.factories.user import SuperUserFactory

    return SuperUserFactory(username="superuser@example.com")


@pytest.fixture()
def organization(db):

    from testutils.factories.org import OrganizationFactory

    return OrganizationFactory(name="OS4D")


@pytest.fixture()
def project(db):
    from testutils.factories.org import ProjectFactory

    return ProjectFactory(name="BITCASTER")


@pytest.fixture()
def application(db):
    from testutils.factories.org import ApplicationFactory

    return ApplicationFactory(name="Bitcaster", project__name="BITCASTER", project__organization__name="OS4D")


@pytest.fixture()
def distributionlist(db):
    from testutils.factories.distribution import DistributionList

    return DistributionList()


@pytest.fixture()
def event(db):
    from testutils.factories.event import EventFactory

    return EventFactory()


@pytest.fixture()
def address(db):
    from testutils.factories.address import AddressFactory

    return AddressFactory()


@pytest.fixture()
def message(db):
    from testutils.factories.message import MessageFactory

    return MessageFactory()


@pytest.fixture()
def channel(db):
    from testutils.factories.channel import ChannelFactory

    return ChannelFactory()


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


@pytest.fixture()
def notification(db):
    from testutils.factories import NotificationFactory

    return NotificationFactory()


@pytest.fixture()
def validation(db):
    from testutils.factories import ValidationFactory

    return ValidationFactory()


@pytest.fixture()
def messagebox():
    import testutils.dispatcher

    testutils.dispatcher.MESSAGES = []
    yield testutils.dispatcher.MESSAGES
    testutils.dispatcher.MESSAGES = []
