from typing import TYPE_CHECKING

import pytest

from django.contrib.auth.models import Group

from bitcaster.utils.constance import EmailChannel, GroupSelect

if TYPE_CHECKING:
    from bitcaster.models import Channel


@pytest.mark.django_db
def test_emailchannel(email_channel: "Channel") -> None:
    fld = EmailChannel()
    assert fld.choices == [(email_channel.pk, email_channel.name)]


@pytest.mark.django_db
def test_groupselect() -> None:
    Group.objects.create(name="TestGroup")
    fld = GroupSelect()
    assert fld.choices == [("TestGroup", "TestGroup")]
