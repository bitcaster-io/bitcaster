from datetime import timedelta

import pytest
from django.contrib.admin.sites import site as admin_site
from django.utils import timezone
from strategy_field.utils import fqn
from testutils.factories import (
    AddressFactory,
    AssignmentFactory,
    ChannelFactory,
    DistributionListFactory,
    NotificationFactory,
    UserMessageFactory,
)

from bitcaster.admin.filters import AddressByList, AddressByNotification, UserMessageExpiredFilter
from bitcaster.dispatchers import UserMessageDispatcher
from bitcaster.models import Address, UserMessage


@pytest.fixture
def dl():
    return DistributionListFactory.create()


@pytest.mark.django_db
def test_user_message_expired_filter(rf):
    ChannelFactory.create(dispatcher=fqn(UserMessageDispatcher), config={"message_ttl": 5})

    now = timezone.now()
    msg_active = UserMessageFactory()
    msg_expired = UserMessageFactory()

    UserMessage.objects.filter(pk=msg_active.pk).update(created=now - timedelta(days=1))
    UserMessage.objects.filter(pk=msg_expired.pk).update(created=now - timedelta(days=10))

    request = rf.get("/")
    f = UserMessageExpiredFilter(request, {"expired": "0"}, UserMessage, admin_site)
    qs = f.queryset(request, UserMessage.objects.all())
    assert msg_expired in qs
    assert msg_active not in qs


@pytest.mark.django_db
def test_address_by_list_filter(rf, dl):
    addr = AddressFactory()
    ass = AssignmentFactory(address=addr)
    dl.recipients.add(ass)

    request = rf.get("/")
    # We need to find the index for our DL in the lookups
    f_dummy = AddressByList(request, {}, Address, admin_site)
    lookups = f_dummy.lookups(request, None)
    index = -1
    for i, (val, __) in enumerate(lookups):
        if val == dl.pk:
            index = i
            break

    assert index != -1

    # Now use the index as the value in the filter
    f = AddressByList(request, {"dl": str(index)}, Address, admin_site)
    qs = f.queryset(request, Address.objects.all())
    assert addr in qs


@pytest.mark.django_db
def test_address_by_notification_filter(rf):
    notif = NotificationFactory()
    addr = AddressFactory()
    ass = AssignmentFactory(address=addr)
    notif.distribution.recipients.add(ass)

    request = rf.get("/")
    f_dummy = AddressByNotification(request, {}, Address, admin_site)
    lookups = f_dummy.lookups(request, None)
    index = -1
    for i, (val, __) in enumerate(lookups):
        if val == notif.pk:
            index = i
            break

    assert index != -1

    f = AddressByNotification(request, {"n": str(index)}, Address, admin_site)
    qs = f.queryset(request, Address.objects.all())
    assert addr in qs
