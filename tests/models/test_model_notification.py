from typing import TYPE_CHECKING, Any, TypedDict
from unittest.mock import Mock

import pytest
from pytest_django import DjangoAssertNumQueries

from bitcaster.models.choices import FILTERING_DYNAMIC, FILTERING_EXTERNAL, FILTERING_NONE

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
        MessageTemplateFactory,
    )

    event: "Event" = EventFactory.create(
        channels=[email_channel], messages=[MessageTemplateFactory(channel=email_channel)]
    )
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
    from testutils.factories import ChannelFactory, MessageTemplateFactory

    ch1 = ChannelFactory()
    m1 = MessageTemplateFactory(channel=ch1, notification=notification, event=notification.event)

    with django_assert_num_queries(1):
        assert notification.get_message(ch1) == m1
        assert notification.get_message(ch1) == m1
        assert notification.get_message(ch1) == m1


def test_get_message_precedence(event: "Event", django_assert_num_queries: DjangoAssertNumQueries) -> None:
    from testutils.factories import ChannelFactory, MessageTemplateFactory, NotificationFactory

    ch1 = ChannelFactory()
    n1: "Notification" = NotificationFactory.create(event=event)
    n2: "Notification" = NotificationFactory.create(event=event)

    m1: "MessageTemplate" = MessageTemplateFactory.create(name="m1", channel=ch1, event=n1.event, notification=None)
    m2: "MessageTemplate" = MessageTemplateFactory.create(name="m2", channel=ch1, event=n1.event, notification=n2)

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
    policy = FILTERING_NONE
    match bool(recipients_filter), bool(api_filters):
        case False, False:
            distribution = data["distribution"]
        case True, __:
            distribution = None
            policy = FILTERING_DYNAMIC
        case __, True:
            distribution = data["distribution"]
            policy = FILTERING_EXTERNAL
        case __:
            distribution = None
    notification = NotificationFactory.create(
        event=data["event"],
        policy=policy,
        distribution=distribution,
        recipients_filter=recipients_filter,
    )
    qs = notification.get_pending_subscriptions(delivered=[], channel=data["channel"], api_filtering=api_filters)
    results = list(qs.values_list("address__value", flat=True))
    assert len(results) == expected, results


@pytest.mark.parametrize(
    "rule, payload, expected",
    [
        # JMESPath inline syntax
        ("country == 'italy'", {"country": "italy"}, True),
        ("country == 'italy'", {"country": "france"}, False),
        (
            "(country == 'italy' && region == 'lazio') || office == `22` ",
            {"country": "italy", "region": "lazio"},
            True,
        ),
        ("(country == 'italy' && region == 'lazio') || office == `22` ", {"office": 22}, True),
        (
            "(country == 'italy' && region == 'lazio') || office == `22` ",
            {"country": "italy", "region": "toscana", "office": 10},
            False,
        ),
        # Structured YAML syntax (AND/OR)
        ("AND:\n  - country == 'italy'\n  - region == 'lazio'", {"country": "italy", "region": "lazio"}, True),
        ("AND:\n  - country == 'italy'\n  - region == 'lazio'", {"country": "italy", "region": "toscana"}, False),
        ("OR:\n  - country == 'italy'\n  - office == `22` ", {"office": 22}, True),
        (
            "OR:\n  - AND:\n      - country == 'italy'\n      - region == 'lazio'\n  - office == `22` ",
            {"country": "italy", "region": "lazio"},
            True,
        ),
        (
            "OR:\n  - AND:\n      - country == 'italy'\n      - region == 'lazio'\n  - office == `22` ",
            {"office": 22},
            True,
        ),
        (
            "OR:\n  - AND:\n      - country == 'italy'\n      - region == 'lazio'\n  - office == `22` ",
            {"country": "italy", "region": "toscana", "office": 10},
            False,
        ),
    ],
)
def test_payload_filter(notification: "Notification", rule: str, payload: dict, expected: bool) -> None:
    notification.payload_filter = rule
    assert notification.match_filter(payload) is expected


@pytest.mark.django_db
def test_get_pending_subscriptions_with_variables(data):
    from testutils.factories import AssignmentFactory, NotificationFactory, UserFactory

    user = UserFactory(username="target_user")
    AssignmentFactory(address__user=user, channel=data["channel"])

    notification = NotificationFactory.create(
        event=data["event"],
        policy=FILTERING_DYNAMIC,
        recipients_filter={"include": {"username": "{{ target_username }}"}},
        distribution=None,
    )

    context = {"target_username": "target_user"}
    qs = notification.get_pending_subscriptions(
        delivered=[], channel=data["channel"], api_filtering={}, context=context
    )

    results = list(qs.values_list("address__user__username", flat=True))
    assert "target_user" in results
    assert len(results) == 1


@pytest.mark.django_db
def test_validate_filters_with_variables():
    from bitcaster.models import User
    from bitcaster.utils.filtering import validate_filters

    # This should not raise FieldError even if {{ var }} is not a valid username
    validate_filters(User.objects.all(), {"include": {"username": "{{ some_var }}"}, "exclude": {}})


@pytest.mark.django_db
def test_render_recursive_nested():
    from testutils.factories import AssignmentFactory, NotificationFactory, UserFactory

    user1 = UserFactory(username="user1")
    user2 = UserFactory(username="user2")

    from bitcaster.models import Channel

    channel = Channel.objects.first()  # assuming one exists from other fixtures
    if not channel:
        from testutils.factories import ChannelFactory

        channel = ChannelFactory()

    AssignmentFactory(address__user=user1, channel=channel)
    AssignmentFactory(address__user=user2, channel=channel)

    notification = NotificationFactory.create(
        policy=FILTERING_DYNAMIC,
        recipients_filter={"include": [{"username": "{{ user_a }}"}, {"username": "{{ user_b }}"}]},
        distribution=None,
    )

    context = {"user_a": "user1", "user_b": "user2"}
    qs = notification.get_pending_subscriptions(delivered=[], channel=channel, api_filtering={}, context=context)

    results = set(qs.values_list("address__user__username", flat=True))
    assert results == {"user1", "user2"}
