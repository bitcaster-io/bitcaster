from datetime import timedelta

import pytest
from testutils.factories import (
    AddressFactory,
    AssignmentFactory,
    ChannelFactory,
    DistributionListFactory,
    NotificationFactory,
    UserMessageFactory,
)

from django.contrib.admin.sites import site as admin_site
from django.utils import timezone
from strategy_field.utils import fqn

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
    other = AddressFactory()
    ass = AssignmentFactory(address=addr)
    dl.recipients.add(ass)

    request = rf.get("/")
    f = AddressByList(request, {"dl": [str(dl.pk)]}, Address, admin_site)
    qs = f.queryset(request, Address.objects.all())
    assert addr in qs
    assert other not in qs

    f = AddressByList(request, {}, Address, admin_site)
    qs = f.queryset(request, Address.objects.all())
    assert addr in qs
    assert other in qs


@pytest.mark.django_db
def test_address_by_notification_filter(rf):
    notif = NotificationFactory()
    addr = AddressFactory()
    other = AddressFactory()
    ass = AssignmentFactory(address=addr)
    notif.distribution.recipients.add(ass)

    request = rf.get("/")
    f = AddressByNotification(request, {"n": [str(notif.pk)]}, Address, admin_site)
    qs = f.queryset(request, Address.objects.all())
    assert addr in qs
    assert other not in qs

    f = AddressByNotification(request, {}, Address, admin_site)
    qs = f.queryset(request, Address.objects.all())
    assert addr in qs
    assert other in qs
