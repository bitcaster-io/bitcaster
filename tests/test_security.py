# -*- coding: utf-8 -*-
import pytest

from bitcaster.backends import (ADMIN_PERMISSIONS, OWNER_PERMISSIONS,
                                BitcasterBackend,)
from bitcaster.db.fields import Role
from bitcaster.models import ApplicationTeam, OrganizationMember, TeamMembership
from bitcaster.utils.tests.factories import TeamFactory, UserFactory


@pytest.fixture
def subscriber1(application1):
    org = application1.organization
    user = UserFactory()
    team = TeamFactory(organization=org, name='Subscribers')
    membership = OrganizationMember.objects.create(organization=org, user=user)
    ApplicationTeam.objects.create(application=application1,
                                   team=team,
                                   role=Role.SUBSCRIBER)
    TeamMembership.objects.create(team=team, member=membership)
    return user

#
# @pytest.fixture
# def member2(organization2):
#     return MemberFactory(organization=organization2)


@pytest.fixture
def admin1(application1):
    org = application1.organization
    user = UserFactory()
    team = TeamFactory(organization=org)
    membership = OrganizationMember.objects.create(organization=org, user=user)
    ApplicationTeam.objects.create(application=application1,
                                   team=team,
                                   role=Role.ADMIN)
    TeamMembership.objects.create(team=team, member=membership)
    return user


@pytest.fixture
def admin2(application2):
    org = application2.organization
    user = UserFactory()
    team = TeamFactory(organization=org)
    membership = OrganizationMember.objects.create(organization=org, user=user)
    ApplicationTeam.objects.create(application=application2,
                                   team=team,
                                   role=Role.ADMIN)
    TeamMembership.objects.create(team=team, member=membership)
    return user


@pytest.mark.django_db
def test_get_all_permisssions(event1, event2, admin, user3, admin1, subscriber1):
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

    assert backend.get_all_permissions(subscriber1, org1) == set()
    assert backend.get_all_permissions(subscriber1, app1) == set()
    assert backend.get_all_permissions(subscriber1, event1) == set()


@pytest.mark.django_db
def test_backend(event1, event2, admin, user3, admin1, admin2):
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
    assert backend.has_perm(admin2, 'evt:trigger', event2)
