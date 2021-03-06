import os
import sys
from pathlib import Path

import pytest
from faker import Faker
from strategy_field.utils import fqn
from vcr import VCR
from webtest import Field as WebTestField, Form

faker = Faker()


def pytest_addoption(parser):
    parser.addoption('--plugins', action='store_true', dest='enable_plugins',
                     default=False, help='enable plugins tests')

    parser.addoption('--paid', action='store_true', dest='enable_paid',
                     default=False, help='enable paid plugins tests')


def pytest_configure(config):
    here = Path(__file__).parent
    root = here.parent
    sys.path.insert(0, str(here / 'extras'))
    sys.path.insert(0, str(root / 'src'))
    # os.environ.setdefault('BITCASTER_CONF', str(here / '.conf'))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bitcaster.config.settings')
    os.environ['CELERY_TASK_ALWAYS_EAGER'] = 'True'
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    os.environ['RECAPTCHA_DISABLE'] = 'True'
    os.environ['BITCASTER_LOG_LEVEL'] = 'ERROR'
    os.environ['BITCASTER_SENTRY_ENABLED'] = '0'
    os.environ['BITCASTER_SENTRY_DSN'] = ''

    os.environ['BITCASTER_REDIS_CACHE_URL'] += '&key_prefix=bitcaster-test'
    os.environ['BITCASTER_REDIS_LOCK_URL'] += '&key_prefix=bitcaster-lock-test'
    os.environ['BITCASTER_REDIS_TSDB_URL'] += '&key_prefix=bitcaster-tsdb-test'

    config.SITE_URL = 'http://testserver/'
    from bitcaster.config.environ import env
    if (here / '.test_env').exists():
        env.load_config(str(here / '.test_env'))
    import django
    django.setup()
    from django.conf import settings
    settings.CACHES['default']['KEY_PREFIX'] = 'test-default'

    from bitcaster.utils.locks import remove_locks
    remove_locks('*')
    os.makedirs('/tmp/static', exist_ok=True)
    os.makedirs('/tmp/media', exist_ok=True)
    # from constance import config as c
    # c.INITIALIZED = True
    settings.CELERY_TASK_ALWAYS_EAGER = True


# @pytest.yield_fixture(scope='session')
# def dddjango_db_setup(request,
#                     django_test_environment,
#                     django_db_blocker,
#                     django_db_use_migrations,
#                     django_db_keepdb,
#                     django_db_createdb,
#                     django_db_modify_db_settings):
#     """Top level fixture to ensure test databases are available"""
#     from pytest_django.compat import setup_databases, teardown_databases
#     from pytest_django.fixtures import _disable_native_migrations
#     setup_databases_args = {}
#
#     if not django_db_use_migrations:
#         _disable_native_migrations()
#
#     if django_db_keepdb and not django_db_createdb:
#         setup_databases_args['keepdb'] = True
#
#     with django_db_blocker.unblock():
#         db_cfg = setup_databases(
#             verbosity=pytest.config.option.verbose,
#             interactive=False,
#             **setup_databases_args
#         )
#
#     def teardown_database():
#         with django_db_blocker.unblock():
#             teardown_databases(db_cfg, verbosity=pytest.config.option.verbose)
#
#     if not django_db_keepdb:
#         request.addfinalizer(teardown_database)
#
#     with django_db_blocker.unblock():
#         from bitcaster.models import DispatcherMetaData, AgentMetaData
#         DispatcherMetaData.objects.inspect()
#         AgentMetaData.objects.inspect()


@pytest.fixture(autouse=True)
def patch(monkeypatch, db, settings):
    monkeypatch.setattr('crashlog.middleware.process_exception',
                        lambda *a, **kw: True)

    monkeypatch.setattr('bitcaster.apps.capture_exception',
                        lambda *a, **kw: True)


@pytest.fixture()
def patch_metadata(monkeypatch):
    from bitcaster.models import DispatcherMetaData, Channel
    monkeypatch.setattr('%s.objects.is_enabled' % fqn(DispatcherMetaData),
                        lambda *a, **kw: True)
    monkeypatch.setattr('%s.objects.enabled' % fqn(DispatcherMetaData),
                        lambda: DispatcherMetaData.objects.all())
    monkeypatch.setattr('%s.objects.selectable' % fqn(Channel),
                        lambda *a, **k: Channel.objects.all())


@pytest.fixture()
def test_dir():
    return str(Path(__file__).parent)


@pytest.fixture(scope='function')
def vcr(request):
    path = str(Path(request.fspath).parent / 'cassetes' / str(request.function.__name__))
    vcr = VCR(cassette_library_dir=path, filter_query_parameters=['access_key'])
    return vcr


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
    from bitcaster.dispatchers import Email
    addresses = {fqn(Email): faker.email()}
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


admin_user = admin


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
    return ChannelFactory(application=application1,
                          organization=application1.organization
                          )


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
def assignment1(user1, channel1):
    from bitcaster.utils.tests.factories import AddressAssignmentFactory, AddressFactory
    return AddressAssignmentFactory(channel=channel1,
                                    user=user1,
                                    address=AddressFactory(user=user1,
                                                           address='address'))


@pytest.fixture
def organization_member(organization1, user1):
    from bitcaster.utils.tests.factories import OrganizationMemberFactory

    return OrganizationMemberFactory(organization=organization1,
                                     user=user1)


@pytest.fixture
def application_member(application1, organization_member):
    from bitcaster.utils.tests.factories import ApplicationMemberFactory

    return ApplicationMemberFactory(application=application1,
                                    org_member=organization_member)


@pytest.fixture
def subscriber1(user1, message1):
    from bitcaster.utils.tests.factories import AddressAssignmentFactory
    for addr in user1.addresses.all():
        AddressAssignmentFactory(user=user1,
                                 address=addr,
                                 channel=message1.channel)
        # user1.assignments.create(address=addr,
        #                          verified=
        #                          channel=message1.channel)
    return user1


@pytest.fixture
def subscriber2(user2, channel1):
    for addr in user2.addresses.all():
        user2.assignments.create(address=addr, channel=channel1)

    return user2


@pytest.fixture
def address1(application1, subscriber1):
    from bitcaster.utils.tests.factories import AddressFactory
    return AddressFactory(user=subscriber1)


@pytest.fixture
def subscription1(application1, subscriber1):
    from bitcaster.utils.tests.factories import SubscriptionFactory
    return SubscriptionFactory(subscriber=subscriber1,
                               event=subscriber1.assignments.first().channel.event_set.first(),
                               channel=subscriber1.assignments.first().channel)


@pytest.fixture
def subscription2(application1, subscriber2):
    from bitcaster.utils.tests.factories import SubscriptionFactory
    return SubscriptionFactory(subscriber=subscriber2,
                               event=subscriber2.assignments.first().channel.event_set.first(),
                               channel=subscriber2.assignments.first().channel)


@pytest.fixture
def notification1(subscription1):
    from bitcaster.utils.tests.factories import NotificationFactory
    return NotificationFactory(id=1,
                               event=subscription1.event,
                               channel=subscription1.channel,
                               subscription=subscription1,
                               application=subscription1.event.application)


@pytest.fixture
def team1(application1):
    from bitcaster.utils.tests.factories import TeamFactory
    return TeamFactory(application=application1)


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


@pytest.fixture
def monitor1(application1):
    from bitcaster.utils.tests.factories import MonitorFactory
    return MonitorFactory(application=application1)


@pytest.fixture
def occurence1(db, event1):
    from bitcaster.utils.tests.factories import OccurenceFactory
    return OccurenceFactory(application=event1.application, event=event1)


@pytest.fixture()
def rf2():
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


@pytest.fixture(autouse=True)
def _check_environ(request):
    marker = request.node.get_closest_marker('skipif_missing')
    if marker:
        missing = [v for v in marker.args if v not in os.environ]
        if missing:
            pytest.skip(f"{','.join(missing)} not found in environment")

    marker = request.node.get_closest_marker('plugin')
    if marker:
        if not pytest.config.option.enable_plugins:
            pytest.skip('Plugins test disabled. Use --plugins to enable them')

    marker = request.node.get_closest_marker('paid')
    if marker:
        if not pytest.config.option.enable_paid:
            pytest.skip('Paid plugins disabled. Use --paid to enable them')
