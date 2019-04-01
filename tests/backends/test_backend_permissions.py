# -*- coding: utf-8 -*-
import pytest
from strategy_field.utils import fqn

from bitcaster.backends import BitcasterBackend
from bitcaster.dispatchers import Email
from bitcaster.framework.db.fields import ROLES
from bitcaster.models import ApplicationMember, OrganizationMember
from bitcaster.utils.tests.factories import (OrganizationMemberFactory,
                                             TeamFactory, UserFactory, faker,)

pytestmark = pytest.mark.django_db


@pytest.fixture
def subscriber11(message1):
    application = message1.event.application
    org = application.organization
    user = UserFactory(addresses={fqn(Email): faker.email()})
    for addr in user.addresses.all():
        user.assignments.create(address=addr, channel=message1.channel)

    TeamFactory(application=application, name='Subscribers')
    membership = OrganizationMember.objects.create(organization=org, user=user)
    ApplicationMember.objects.create(application=application, org_member=membership)
    # team.members.add(membership)
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
    assert b.has_perm(org.owner, 'manage_organization', org)
    assert b.has_perm(org.owner, 'manage_application', app)

    assert not b.has_perm(subscriber, 'manage_application', app)
    assert not b.has_perm(org.owner, 'manage_application')
    assert b.has_perm(org.owner, 'manage_application', object()) is None


#
# @pytest.fixture
# def member2(organization2):
#     return MemberFactory(organization=organization2)


@pytest.fixture
def admin1(application1):
    org = application1.organization
    user = UserFactory()
    OrganizationMemberFactory(organization=org, user=user,
                              role=ROLES.ADMIN)
    return user


@pytest.fixture
def admin2(application2):
    org = application2.organization
    user = UserFactory()
    team = TeamFactory(application=application2, name='Subscribers', role=ROLES.MEMBER)
    membership, __ = OrganizationMember.objects.get_or_create(organization=org, user=user)
    team.members.add(membership)
    return user


# @pytest.mark.django_db
# def test_get_all_permisssions(event1, event2, admin, user3, admin1, subscriber11):
#     backend = BitcasterBackend()
#     app1 = event1.application
#     org1 = app1.organization
#     # owner1 = org1.owner
#
#     # assert backend.get_all_permissions(owner1, org1) == OWNER_PERMISSIONS
#     # assert backend.get_all_permissions(owner1, app1) == OWNER_PERMISSIONS
#
#     assert backend.get_all_permissions(admin1, org1) == set()
#     assert backend.get_all_permissions(admin1, app1) == ADMIN_PERMISSIONS
