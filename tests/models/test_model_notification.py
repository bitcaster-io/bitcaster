from typing import TYPE_CHECKING, Any, TypedDict
from unittest.mock import Mock

import pytest
from pytest_django import DjangoAssertNumQueries

if TYPE_CHECKING:
    from bitcaster.models import (
        ApiKey,
        Assignment,
        Channel,
        DistributionList,
        Event,
        MessageTemplate,
        Notification,
        User,
    )

    Context = TypedDict(
        "Context",
        {
            "event": Event,
            "key": ApiKey,
            "user": User,
            "channel": Channel,
            "distribution": DistributionList,
            "assignments": list[Assignment],
        },
    )


@pytest.fixture
def data(admin_user: "User", email_channel: "Channel") -> "Context":
    from testutils.factories import (
        ApiKeyFactory,
        AssignmentFactory,
        DistributionListFactory,
        EventFactory,
        MessageFactory,
    )

    event: "Event" = EventFactory.create(channels=[email_channel], messages=[MessageFactory(channel=email_channel)])
    assignments = [
        AssignmentFactory.create(address__value=f"email-{i:02}@d{i % 2:02}.com", channel=email_channel)
        for i in range(1, 11)
    ]
    distribution = DistributionListFactory.create(recipients=assignments)
    key = ApiKeyFactory.create(user=admin_user, grants=[], application=event.application)
    return {
        "event": event,
        "key": key,
        "user": admin_user,
        "distribution": distribution,
        "assignments": assignments,
        "channel": email_channel,
    }


def test_get_message_cache(notification: "Notification", django_assert_num_queries: DjangoAssertNumQueries) -> None:
    from testutils.factories import ChannelFactory, MessageFactory

    ch1 = ChannelFactory()
    m1 = MessageFactory(channel=ch1, notification=notification, event=notification.event)

    with django_assert_num_queries(1):
        assert notification.get_message(ch1) == m1
        assert notification.get_message(ch1) == m1
        assert notification.get_message(ch1) == m1


def test_get_message_precedence(event: "Event", django_assert_num_queries: DjangoAssertNumQueries) -> None:
    from testutils.factories import ChannelFactory, MessageFactory, NotificationFactory

    ch1 = ChannelFactory()
    n1: "Notification" = NotificationFactory.create(event=event)
    n2: "Notification" = NotificationFactory.create(event=event)

    m1: "MessageTemplate" = MessageFactory.create(name="m1", channel=ch1, event=n1.event, notification=None)
    m2: "MessageTemplate" = MessageFactory.create(name="m2", channel=ch1, event=n1.event, notification=n2)

    assert list(n1.get_messages(ch1)) == [m1]
    assert list(n2.get_messages(ch1)) == [m2, m1]

    with django_assert_num_queries(2):
        assert n1.get_message(ch1) == m1
        assert n1.get_message(ch1) == m1

        assert n2.get_message(ch1) == m2
        assert n2.get_message(ch1) == m2


def test_missing_message(event: "Event", monkeypatch: pytest.MonkeyPatch) -> None:
    from testutils.factories import ChannelFactory, NotificationFactory

    ch1 = ChannelFactory.create()
    n1: "Notification" = NotificationFactory.create(event=event)
    monkeypatch.setattr(ch1.dispatcher, "send", mocked_notify := Mock())

    ret, __ = n1.notify_to_channel(ch1, Mock(), {})
    assert ret is None
    assert mocked_notify.call_count == 0


@pytest.mark.parametrize(
    "ctx, extra, expected",
    [
        pytest.param({}, {}, {}, id="all-empty"),
        pytest.param({}, {"new": 123}, {"new": 123}, id="contribute"),
        pytest.param({"a": 1, "b": 2, "c": 3}, {"b": 99}, {"a": 1, "b": 99, "c": 3}, id="override-b"),
        pytest.param({"a": 1, "b": 2}, {}, {"a": 1, "b": 2}, id="no-override"),
        pytest.param({"notification": 1, "b": 2}, {}, {"b": 2}, id="override-element"),
    ],
)
def test_extra_context_override(ctx: dict[str, str], extra: dict[str, Any], expected: dict[str, Any]) -> None:
    from testutils.factories import NotificationFactory

    notification = NotificationFactory.create(extra_context=extra)
    expected |= {"notification": notification}
    assert notification.get_context(ctx).items() >= expected.items()


@pytest.mark.parametrize(
    "recipients_filter, api_filters, expected",
    [
        pytest.param({}, {}, 10, id="api-filtered-full"),
        pytest.param({}, {"include": [{"addresses__value": "email-01@d01.com"}]}, 1, id="api-filtered-1"),
        pytest.param({}, {"exclude": [{"addresses__value": "email-01@d01.com"}]}, 9, id="api-filtered-2"),
        pytest.param({}, {"include": [{"addresses__value__contains": "@d00.com"}]}, 5, id="api-filtered-3"),
        pytest.param({"include": [{"addresses__value": "email-01@d01.com"}]}, {}, 1, id="api-filtered-4"),
    ],
)
def test_get_pending_subscriptions(data: "Context", recipients_filter, api_filters, expected) -> None:
    from testutils.factories import NotificationFactory

    distribution = None
    external_filtering = False
    dynamic = False
    match bool(recipients_filter), bool(api_filters):
        case False, False:
            distribution = data["distribution"]
        case True, __:
            distribution = None
            dynamic = True
        case __, True:
            distribution = data["distribution"]
            external_filtering = True
        case __:
            distribution = None
    notification = NotificationFactory.create(
        event=data["event"],
        external_filtering=external_filtering,
        dynamic=dynamic,
        distribution=distribution,
        recipients_filter=recipients_filter,
    )
    qs = notification.get_pending_subscriptions(delivered=[], channel=data["channel"], api_filtering=api_filters)
    results = list(qs.values_list("address__value", flat=True))
    assert len(results) == expected, results
