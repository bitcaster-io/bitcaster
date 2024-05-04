from typing import Any, Dict, Optional

import pytest

EXAMPLE_PAYLOAD = {
    "people": [
        {
            "general": {"id": 100, "age": 20, "other": "foo", "name": "Bob"},
            "history": {"first_login": "2014-01-01", "last_login": "2014-01-02"},
        },
        {
            "general": {"id": 101, "age": 30, "other": "bar", "name": "Bill"},
            "history": {"first_login": "2014-05-01", "last_login": "2014-05-02"},
        },
    ]
}


@pytest.mark.parametrize("statement", ["AND", "OR"])
def test_simple_filter(statement):
    from bitcaster.models import Notification

    # now we test a non-matching filter
    result = Notification.match_filter_impl(
        {"{statement}": ["people[?general.id==`999`].general | [0]"]}, EXAMPLE_PAYLOAD
    )

    assert result is False


def test_plain_filter():
    # now we test a matching filter
    from bitcaster.models import Notification

    result = Notification.match_filter_impl("status == 'terminated: completed'", {"status": "terminated: completed"})

    assert result is True


@pytest.mark.parametrize(
    "payload, matches",
    [
        pytest.param({}, False, id="empty"),
        pytest.param({"foo": "doo"}, False, id="wrong"),
        pytest.param({"foo": "bar"}, True, id="ok"),
    ],
)
def test_queryset_filter(db, payload: Dict, matches: bool):
    from testutils.factories import NotificationFactory

    from bitcaster.models import Notification

    sub1 = NotificationFactory()
    sub2 = NotificationFactory(event=sub1.event, payload_filter="foo=='bar'")

    m = list([m.id for m in Notification.objects.match(payload)])
    assert m == [sub1.id] + ([sub2.id] if matches else [])


@pytest.mark.parametrize(
    "filter, result",
    [
        pytest.param({"OR": ["foo=='doo'", "foo=='bar'"]}, True, id="or"),
        pytest.param({"AND": ["foo=='doo'", "foo=='bar'"]}, False, id="and"),
        pytest.param({"NOT": "foo=='doo'"}, True, id="not-ok"),
        pytest.param({"NOT": "foo=='bar'"}, False, id="not-nok"),
        pytest.param({}, True, id="empty"),
    ],
)
def test_jmespath_filter(db, filter: Optional[Dict[str, Any] | str], result: bool):
    from bitcaster.models import Notification

    assert Notification.match_filter_impl(filter_rules_dict=filter, payload={"foo": "bar"}) is result


@pytest.mark.parametrize(
    "filter, result",
    [
        pytest.param({"OR": ["foo=='doo'", "foo=='bar'"]}, True, id="or"),
        pytest.param({"AND": ["foo=='doo'", "foo=='bar'"]}, False, id="and"),
        pytest.param({"NOT": "foo=='doo'"}, True, id="not-ok"),
        pytest.param({"NOT": "foo=='bar'"}, False, id="not-nok"),
        pytest.param({}, True, id="empty"),
    ],
)
def test_match_filter(db, filter: Optional[Dict[str, Any] | str], result: bool):
    from bitcaster.models import Notification

    assert Notification().match_filter(rules=filter, payload={"foo": "bar"}) is result
