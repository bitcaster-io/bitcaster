from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from bitcaster.models import Channel, Organization, User


@pytest.fixture
def org_user(organization: "Organization") -> "User":
    from testutils.factories import UserRole, UserRoleFactory

    r: UserRole = UserRoleFactory(organization=organization)
    return r.user


@pytest.fixture
def org_channel(organization: "Organization") -> "Channel":
    from testutils.factories import ChannelFactory

    return ChannelFactory(organization=organization, project=None)
