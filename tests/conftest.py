import os
import sys
from pathlib import Path

import pytest
from faker import Faker
from strategy_field.utils import fqn
from webtest import Field as WebTestField, Form

faker = Faker()


def pytest_configure(config):
    here = Path(__file__).parent
    root = here.parent
    sys.path.insert(0, str(here / 'extras'))
    sys.path.insert(0, str(root / 'src'))
    os.environ.setdefault('BITCASTER_CONF', str(here / '.conf'))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bitcaster.config.settings')
    os.environ['CELERY_TASK_ALWAYS_EAGER'] = 'True'
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    os.environ['RECAPTCHA_DISABLE'] = 'True'
    os.environ['BITCASTER_LOG_LEVEL'] = 'ERROR'
    os.environ['DEBUG_TOOLBAR'] = '1'
    from bitcaster.config.environ import env
    env.load_config(str(here / '.conf'))
    import django
    django.setup()
    from django.conf import settings
    os.makedirs('/tmp/static', exist_ok=True)
    # from constance import config as c
    # c.INITIALIZED = True
    settings.CELERY_TASK_ALWAYS_EAGER = True


@pytest.fixture(autouse=True)
def patch(monkeypatch, db, settings):
    pass


#     monkeypatch.setattr('bitcaster.utils.locks.get', lambda key, duration: Mock())


@pytest.fixture
def initialized(db, monkeypatch):
    monkeypatch.setattr('constance.config.INITIALIZED', True)


@pytest.fixture
def user1(db, initialized):
    from bitcaster.utils.tests.factories import UserFactory
    from bitcaster.dispatchers import Email
    addresses = {fqn(Email): faker.email()}
    return UserFactory(addresses=addresses)


@pytest.fixture
def user2(db):
    from bitcaster.utils.tests.factories import UserFactory
    addresses = {}
    return UserFactory(addresses=addresses)


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
    evt = EventFactory(application=channel1.application, enabled=True)
    evt.channels.add(channel1)
    return evt


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
def subscription1(application1, message1):
    from bitcaster.utils.tests.factories import SubscriptionFactory, UserFactory
    from bitcaster.dispatchers import Email

    return SubscriptionFactory(subscriber=UserFactory(addresses={fqn(Email): faker.email()}),
                               event=message1.event,
                               channel=message1.channel)


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


@pytest.fixture()
def rf():
    from django.test.client import RequestFactory
    from django.contrib.auth.models import AnonymousUser

    class BRequestFactory(RequestFactory):

        def generic(self, method, path, data='', content_type='application/octet-stream', secure=False, **extra):
            ret = super().generic(method, path, data, content_type, secure, **extra)
            ret.user = AnonymousUser()
            ret._messages = []
            ret._alarms = []
            return ret

    return BRequestFactory()


def add_extra_form_to_formset_with_data(form, prefix, field_names_and_values):
    total_forms_field_name = prefix + '-TOTAL_FORMS'
    next_form_index = int(form[total_forms_field_name].value)
    for extra_field_name, extra_field_value in field_names_and_values.items():
        input_field_name = '-'.join((prefix, str(next_form_index), extra_field_name))
        extra_field = WebTestField(form, tag='input', name=input_field_name, pos=0, value=extra_field_value)
        form.fields[input_field_name] = [extra_field]
        form[input_field_name] = extra_field_value
        form.field_order.append((input_field_name, extra_field))
        form[total_forms_field_name].value = str(next_form_index + 1)


# Form.add_extra_form_to_formset_with_data = add_extra_form_to_formset_with_data
Form.add_formset_field = add_extra_form_to_formset_with_data
