from typing import TYPE_CHECKING, TypedDict

import pytest
from unittest.mock import Mock

from django.core.exceptions import ValidationError

from bitcaster.models.choices import FILTERING_DYNAMIC, FILTERING_SUBSCRIPTION

if TYPE_CHECKING:
    from bitcaster.models import (
        Assignment,
        Channel,
        DistributionList,
        MessageTemplate,
        Notification,
        Subscription,
    )

    class SubscriptionData(TypedDict):
        notification: Notification
        assignment: Assignment
        subscription: Subscription
        distribution: DistributionList
        channel: Channel
        message_template: MessageTemplate


@pytest.fixture
def data(email_channel: "Channel") -> "SubscriptionData":
    from testutils.factories import (
        AssignmentFactory,
        DistributionListFactory,
        MessageTemplateFactory,
        NotificationFactory,
        SubscriptionFactory,
    )

    notification: Notification = NotificationFactory.create(
        event__channels=[email_channel],
        policy=FILTERING_SUBSCRIPTION,
        distribution=None,
    )
    assignment: Assignment = AssignmentFactory.create(channel=email_channel)
    subscription: Subscription = SubscriptionFactory.create(notification=notification, assignment=assignment)
    MessageTemplateFactory(channel=email_channel, event=notification.event)
    distribution = DistributionListFactory.create(recipients=[AssignmentFactory.create(channel=email_channel)])

    return {
        "notification": notification,
        "assignment": assignment,
        "subscription": subscription,
        "distribution": distribution,
        "channel": email_channel,
        "message_template": notification.get_message(email_channel),
    }


@pytest.mark.django_db
def test_str(data: "SubscriptionData") -> None:
    assert str(data["subscription"]) == f"{data['assignment']} - {data['notification']}"


@pytest.mark.django_db
def test_user(data: "SubscriptionData") -> None:
    assert data["subscription"].user == data["assignment"].address.user


@pytest.mark.django_db
def test_clean_duplicate_same_channel(data: "SubscriptionData") -> None:
    from testutils.factories import AssignmentFactory, SubscriptionFactory

    other_assignment = AssignmentFactory.create(channel=data["channel"])
    duplicate = SubscriptionFactory.build(notification=data["notification"], assignment=other_assignment)
    with pytest.raises(ValidationError):
        duplicate.clean()


@pytest.mark.django_db
def test_clean_duplicate_ignores_active(data: "SubscriptionData") -> None:
    """`active` is not part of the unique key: an inactive subscription still blocks the pair."""
    from testutils.factories import AssignmentFactory, SubscriptionFactory

    other_assignment = AssignmentFactory.create(channel=data["channel"])
    SubscriptionFactory.create(notification=data["notification"], assignment=other_assignment, active=False)
    duplicate = SubscriptionFactory.build(notification=data["notification"], assignment=other_assignment)
    with pytest.raises(ValidationError):
        duplicate.clean()


@pytest.mark.django_db
def test_clean_different_channel_allowed(data: "SubscriptionData") -> None:
    from testutils.factories import AssignmentFactory, ChannelFactory, SubscriptionFactory

    other_channel = ChannelFactory.create()
    other_assignment = AssignmentFactory.create(channel=other_channel)
    duplicate = SubscriptionFactory.build(notification=data["notification"], assignment=other_assignment)
    duplicate.clean()


@pytest.mark.django_db
def test_clean_own_record_allowed(data: "SubscriptionData") -> None:
    data["subscription"].clean()


@pytest.mark.django_db
def test_clean_without_relations_allowed(data: "SubscriptionData") -> None:
    from testutils.factories import SubscriptionFactory

    partial = SubscriptionFactory.build(notification=None, assignment=None)
    partial.clean()


@pytest.mark.django_db
def test_cascade_delete_assignment(data: "SubscriptionData") -> None:
    from bitcaster.models import Subscription

    data["assignment"].delete()
    with pytest.raises(Subscription.DoesNotExist):
        data["subscription"].refresh_from_db()


@pytest.mark.django_db
def test_cascade_delete_notification(data: "SubscriptionData") -> None:
    from bitcaster.models import Subscription

    data["notification"].delete()
    with pytest.raises(Subscription.DoesNotExist):
        data["subscription"].refresh_from_db()


@pytest.mark.django_db
def test_natural_key(data: "SubscriptionData") -> None:
    from bitcaster.models import Subscription

    assert Subscription.objects.get_by_natural_key(*data["subscription"].natural_key()) == data["subscription"]


@pytest.mark.django_db
def test_get_pending_subscriptions(data: "SubscriptionData") -> None:
    from testutils.factories import (
        AssignmentFactory,
        ChannelFactory,
        SubscriptionFactory,
    )

    channel = data["channel"]
    notification = data["notification"]
    other_channel = ChannelFactory.create()

    active_sub = AssignmentFactory.create(channel=channel)
    SubscriptionFactory.create(notification=notification, assignment=active_sub)
    inactive_sub_assignment = AssignmentFactory.create(channel=channel)
    SubscriptionFactory.create(notification=notification, assignment=inactive_sub_assignment, active=False)
    inactive_assignment = AssignmentFactory.create(channel=channel, active=False)
    SubscriptionFactory.create(notification=notification, assignment=inactive_assignment)
    other_channel_assignment = AssignmentFactory.create(channel=other_channel)
    SubscriptionFactory.create(notification=notification, assignment=other_channel_assignment)
    delivered_assignment = AssignmentFactory.create(channel=channel)
    SubscriptionFactory.create(notification=notification, assignment=delivered_assignment)

    results = notification.get_pending_subscriptions([], channel, {})
    assert set(results) == {data["assignment"], active_sub, delivered_assignment}

    results = notification.get_pending_subscriptions([data["assignment"].pk], channel, {})
    assert set(results) == {active_sub, delivered_assignment}


@pytest.mark.django_db
def test_subscription_policy_ignores_other_sources(data: "SubscriptionData") -> None:
    """FILTERING_SUBSCRIPTION ignores distribution, stored recipients_filter and API filters."""
    from testutils.factories import AssignmentFactory, SubscriptionFactory

    channel = data["channel"]
    notification = data["notification"]
    notification.distribution = data["distribution"]
    notification.recipients_filter = {"include": [{"username": "nobody"}]}
    notification.save()

    subscribed = AssignmentFactory.create(channel=channel)
    SubscriptionFactory.create(notification=notification, assignment=subscribed)

    api_filters = {"include": [{"username": "nobody"}]}
    results = notification.get_pending_subscriptions([], channel, api_filters)
    assert set(results) == {data["assignment"], subscribed}


@pytest.mark.django_db
def test_dynamic_policy_ignores_subscriptions(data: "SubscriptionData") -> None:
    """Subscriptions are only used by FILTERING_SUBSCRIPTION policy."""

    notification: Notification = data["notification"]
    notification.policy = FILTERING_DYNAMIC
    notification.recipients_filter = {"include": [{"username": data["assignment"].address.user.username}]}
    notification.save()

    results = notification.get_pending_subscriptions([], data["channel"], {})
    assert set(results) == {data["assignment"]}


@pytest.mark.django_db
def test_occurrence_subscription_policy(data: "SubscriptionData", monkeypatch: pytest.MonkeyPatch) -> None:
    from testutils.factories import AssignmentFactory, SubscriptionFactory

    notification = data["notification"]
    monkeypatch.setattr(
        "bitcaster.models.notification.Notification.notify_to_channel", mock := Mock(return_value=(None, 999))
    )
    notification.distribution = data["distribution"]
    notification.save()

    subscribed = AssignmentFactory.create(channel=data["channel"])
    SubscriptionFactory.create(notification=notification, assignment=subscribed)

    occurrence = notification.event.trigger(context={"foo": "bar"})
    occurrence.process()

    assert mock.call_count == 2
    occurrence.refresh_from_db()
    assert set(occurrence.data["delivered"]) == {data["assignment"].pk, subscribed.pk}
