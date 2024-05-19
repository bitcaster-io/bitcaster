from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from bitcaster.models import Channel, User


@pytest.fixture
def org_user(organization) -> "User":
    from testutils.factories import UserRole, UserRoleFactory

    r: UserRole = UserRoleFactory(organization=organization)
    return r.user


@pytest.fixture
def org_channel(organization) -> "Channel":
    from testutils.factories import ChannelFactory

    return ChannelFactory(organization=organization, project=None)
