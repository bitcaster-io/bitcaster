# -*- coding: utf-8 -*-
import pytest
from strategy_field.utils import fqn

from bitcaster.backends import (ADMIN_PERMISSIONS, OWNER_PERMISSIONS,
                                BitcasterBackend,)
from bitcaster.db.fields import Role
from bitcaster.dispatchers import Email
from bitcaster.models import ApplicationRole, OrganizationMember
from bitcaster.utils.tests.factories import TeamFactory, UserFactory, faker

pytestmark = pytest.mark.django_db


@pytest.fixture
def subscriber11(message1):
    application = message1.event.application
    org = application.organization
    user = UserFactory(addresses={fqn(Email): faker.email()})
    for addr in user.addresses.all():
        user.assignments.create(address=addr, channel=message1.channel)

    team = TeamFactory(organization=org, name='Subscribers')
    membership = OrganizationMember.objects.create(organization=org, user=user)
    ApplicationRole.objects.create(application=application,
                                   team=team,
                                   role=Role.SUBSCRIBER)
    team.members.add(membership)
    return user


@pytest.fixture
def subscription11(application1, subscriber11):
    from bitcaster.utils.tests.factories import SubscriptionFactory
    return SubscriptionFactory(subscriber=subscriber11,
                               event=subscriber11.assignments.first().channel.event_set.first(),
                               channel=subscriber11.assignments.first().channel)


def test_backend(subscription11):
    event = subscription11.event
    app = event.application
    org = app.organization
    subscriber = subscription11.subscriber

    b = BitcasterBackend()
    assert b.has_perm(org.owner, 'org:configure', org)
    assert b.has_perm(org.owner, 'app:configure', app)

    assert not b.has_perm(subscriber, 'app:configure', app)
    assert not b.has_perm(org.owner, 'app:configure')
    assert b.has_perm(org.owner, 'app:configure', object()) is None


#
# @pytest.fixture
# def member2(organization2):
#     return MemberFactory(organization=organization2)


@pytest.fixture
def admin1(application1):
    org = application1.organization
    user = UserFactory()
    team = TeamFactory(organization=org)
    membership, __ = OrganizationMember.objects.get_or_create(organization=org, user=user)
    ApplicationRole.objects.get_or_create(application=application1,
                                          team=team,
                                          role=Role.ADMIN)
    team.members.add(membership)
    return user


@pytest.fixture
def admin2(application2):
    org = application2.organization
    user = UserFactory()
    team = TeamFactory(organization=org)
    OrganizationMember.objects.get_or_create(organization=org, user=user)
    ApplicationRole.objects.get_or_create(application=application2,
                                          team=team,
                                          role=Role.ADMIN)
    return user


@pytest.mark.django_db
def test_get_all_permisssions(event1, event2, admin, user3, admin1, subscriber11):
    backend = BitcasterBackend()
    app1 = event1.application
    org1 = app1.organization
    owner1 = org1.owner

    assert backend.get_all_permissions(owner1, org1) == OWNER_PERMISSIONS
    assert backend.get_all_permissions(owner1, app1) == OWNER_PERMISSIONS
    assert backend.get_all_permissions(owner1, event1) == OWNER_PERMISSIONS

    assert backend.get_all_permissions(admin1, org1) == set()
    assert backend.get_all_permissions(admin1, app1) == ADMIN_PERMISSIONS
    assert backend.get_all_permissions(admin1, event1) == ADMIN_PERMISSIONS

    assert backend.get_all_permissions(subscriber11, org1) == set()
    assert backend.get_all_permissions(subscriber11, app1) == set()
    assert backend.get_all_permissions(subscriber11, event1) == set()


@pytest.mark.django_db
def test_backend2(event1, event2, admin, user3, admin1, admin2):
    backend = BitcasterBackend()

    app1 = event1.application
    app2 = event2.application

    org1 = app1.organization
    org2 = app2.organization

    owner1 = org1.owner
    owner2 = org2.owner

    assert backend.has_perm(owner1, 'evt:trigger', event1)
    assert backend.has_perm(admin1, 'evt:trigger', event1)
    assert not backend.has_perm(owner2, 'evt:trigger', event1)
    assert not backend.has_perm(admin2, 'evt:trigger', event1)

    assert backend.has_perm(owner2, 'evt:trigger', event2)
    # assert backend.has_perm(admin2, 'evt:trigger', event2)
