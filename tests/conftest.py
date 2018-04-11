import os
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest


def pytest_configure(config):
    here = os.path.dirname(__file__)
    sys.path.insert(0, os.path.join(here, 'extras'))
    os.environ.setdefault('BITCASTER_CONF', str(Path(__file__).parent / '.conf'))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bitcaster.config.settings.default')
    os.environ['CELERY_TASK_ALWAYS_EAGER'] = 'True'
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    os.environ['RECAPTCHA_DISABLE'] = 'True'
    from bitcaster.config.environ import env
    env.load_config(str(Path(__file__).parent / '.conf'))
    import django
    django.setup()
    from django.conf import settings

    # from constance import config as c
    # c.INITIALIZED = True
    settings.CELERY_TASK_ALWAYS_EAGER = True


@pytest.fixture(autouse=True)
def patch(monkeypatch, db):
    monkeypatch.setattr('bitcaster.utils.locks.get', lambda key, duration: Mock())


@pytest.fixture
def initialized(db, monkeypatch):
    monkeypatch.setattr('constance.config.INITIALIZED', True)


@pytest.fixture
def user1(db, initialized):
    from bitcaster.utils.tests.factories import UserFactory
    return UserFactory()


@pytest.fixture
def user2(db):
    from bitcaster.utils.tests.factories import UserFactory

    return UserFactory()


@pytest.fixture
def user3(db):
    from bitcaster.utils.tests.factories import UserFactory

    return UserFactory()


@pytest.fixture
def admin(db, initialized):
    # pytest `django_admin` fixture cannot be used because
    # we do not have username field
    from bitcaster.utils.tests.factories import AdminFactory
    return AdminFactory()


@pytest.fixture
def organization1(user1):
    from bitcaster.utils.tests.factories import OrganizationFactory
    return OrganizationFactory(owner=user1)


@pytest.fixture
def organization2(user2):
    from bitcaster.utils.tests.factories import OrganizationFactory
    return OrganizationFactory(owner=user2)


@pytest.fixture
def application1(organization1):
    from bitcaster.utils.tests.factories import ApplicationFactory
    return ApplicationFactory(organization=organization1)


@pytest.fixture
def maintaner1(application1):
    from bitcaster.utils.tests.factories import UserFactory
    u = UserFactory()
    application1.maintainers.add(u)
    return u


@pytest.fixture
def application2(organization2):
    from bitcaster.utils.tests.factories import ApplicationFactory
    return ApplicationFactory(organization=organization2)


@pytest.fixture
def channel1(application1):
    from bitcaster.utils.tests.factories import ChannelFactory
    return ChannelFactory(application=application1)


@pytest.fixture
def channel2(application2):
    from bitcaster.utils.tests.factories import ChannelFactory
    return ChannelFactory(application=application2)


@pytest.fixture
def event1(channel1):
    from bitcaster.utils.tests.factories import EventFactory
    return EventFactory(application=channel1.application, enabled=True)


@pytest.fixture
def event2(channel2):
    from bitcaster.utils.tests.factories import EventFactory
    return EventFactory(application=channel2.application, enabled=True)


@pytest.fixture
def message1(event1, channel1):
    from bitcaster.utils.tests.factories import MessageFactory
    return MessageFactory(event=event1, channel=channel1)


@pytest.fixture
def message2(event2):
    from bitcaster.utils.tests.factories import MessageFactory
    return MessageFactory(event=event2)


@pytest.fixture
def subscription1(user1, channel1, message1):
    from bitcaster.utils.tests.factories import SubscriptionFactory
    return SubscriptionFactory(subscriber=user1,
                               event=message1.event,
                               channel=channel1)


@pytest.fixture
def subscription2(user2, channel2, message2):
    from bitcaster.utils.tests.factories import SubscriptionFactory
    return SubscriptionFactory(subscriber=user2)


@pytest.fixture
def token1(db):
    from bitcaster.utils.tests.factories import ApiTokenFactory
    return ApiTokenFactory()


@pytest.fixture
def system_channel(db):
    from bitcaster.utils.tests.factories import ChannelFactory
    return ChannelFactory(application=None, system=True)


@pytest.fixture
def org_channel(db, organization1):
    from bitcaster.utils.tests.factories import ChannelFactory
    return ChannelFactory(organization=organization1,
                          application=None, system=False)
