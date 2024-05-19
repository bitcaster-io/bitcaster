from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from bitcaster.models import Address, Assignment, Channel


def test_assignment(db):
    from testutils.factories import AssignmentFactory

    v: "Assignment" = AssignmentFactory()

    ch: "Channel" = v.channel
    addr: "Address" = v.address

    assert list(addr.channels.all()) == [ch]


@pytest.mark.parametrize("args", [{}, {"project": None}])
def test_natural_key(args):
    from testutils.factories import Assignment, AssignmentFactory, ChannelFactory

    msg = AssignmentFactory(channel=ChannelFactory(**args))
    assert Assignment.objects.get_by_natural_key(*msg.natural_key()) == msg, msg.natural_key()
