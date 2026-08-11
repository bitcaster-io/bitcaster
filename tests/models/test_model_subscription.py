from typing import TYPE_CHECKING, TypedDict

import pytest

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
def data() -> "SubscriptionData":
    from testutils.factories import (
        AssignmentFactory,
        ChannelFactory,
        DistributionListFactory,
        MessageTemplateFactory,
        NotificationFactory,
        SubscriptionFactory,
    )

    channel: Channel = ChannelFactory()
    notification: Notification = NotificationFactory.create(
        event__channels=[channel],
        policy=FILTERING_SUBSCRIPTION,
        distribution=None,
    )
    assignment: Assignment = AssignmentFactory.create(channel=channel)
    subscription: Subscription = SubscriptionFactory.create(notification=notification, assignment=assignment)
    MessageTemplateFactory(channel=channel, event=notification.event)
    distribution = DistributionListFactory.create(recipients=[AssignmentFactory.create(channel=channel)])

    return {
        "notification": notification,
        "assignment": assignment,
        "subscription": subscription,
        "distribution": distribution,
        "channel": channel,
        "message_template": notification.get_message(channel),
    }


@pytest.mark.django_db
def test_str(data: "SubscriptionData") -> None:
    assert str(data["subscription"]) == f"{data['assignment']} - {data['notification']}"


@pytest.mark.django_db
def test_user(data: "SubscriptionData") -> None:
    assert data["subscription"].user == data["assignment"].address.user


@pytest.mark.django_db
def test_is_valid(data: "SubscriptionData") -> None:
    assert data["subscription"].is_valid is True
    assert "Invalid" not in str(data["subscription"].validity)


@pytest.mark.django_db
def test_is_valid_channel_not_enabled() -> None:
    from testutils.factories import AssignmentFactory, ChannelFactory, NotificationFactory, SubscriptionFactory

    channel = ChannelFactory()
    notification = NotificationFactory(event__channels=[], distribution=None)
    assignment = AssignmentFactory(channel=channel)
    subscription = SubscriptionFactory(notification=notification, assignment=assignment)

    assert subscription.is_valid is False
    assert "Invalid" in str(subscription.validity)


@pytest.mark.django_db
def test_unique_constraint_same_assignment(data: "SubscriptionData") -> None:
    """The DB unique constraint prevents duplicate (notification, assignment) pairs."""
    from django.db import IntegrityError

    from bitcaster.models import Subscription

    with pytest.raises(IntegrityError):
        Subscription.objects.create(notification=data["notification"], assignment=data["assignment"])


@pytest.mark.django_db
def test_unique_constraint_allows_different_assignment_same_channel(data: "SubscriptionData") -> None:
    """Different assignments on the same channel for the same notification are allowed."""
    from testutils.factories import AssignmentFactory, SubscriptionFactory

    other_assignment = AssignmentFactory.create(channel=data["channel"])
    other = SubscriptionFactory.create(notification=data["notification"], assignment=other_assignment)
    assert other.pk is not None


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
    notification.distribution = data["distribution"]
    notification.save()

    subscribed = AssignmentFactory.create(channel=data["channel"])
    SubscriptionFactory.create(notification=notification, assignment=subscribed)

    occurrence = notification.event.trigger(context={"foo": "bar"})
    occurrence.process()

    occurrence.refresh_from_db()
    assert occurrence.recipients == 2
    assert occurrence.deliveries.count() == 2
    assert set(occurrence.deliveries.values_list("assignment_id", flat=True)) == {data["assignment"].pk, subscribed.pk}
