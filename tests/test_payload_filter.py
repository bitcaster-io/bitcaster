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

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    "payload, matches",
    [
        pytest.param({}, False, id="empty"),
        pytest.param({"foo": "doo"}, False, id="wrong"),
        pytest.param({"foo": "bar"}, True, id="ok"),
    ],
)
def test_queryset_filter(payload: Dict[str, str], matches: bool) -> None:
    from testutils.factories import NotificationFactory

    from bitcaster.models import Notification

    sub1 = NotificationFactory()
    sub2 = NotificationFactory(event=sub1.event, payload_filter="foo=='bar'")

    m = [m.id for m in Notification.objects.match(payload)]
    assert m == [sub1.id] + ([sub2.id] if matches else [])


@pytest.mark.parametrize(
    "filter_rules, result",
    [
        pytest.param({"OR": ["foo=='doo'", "foo=='bar'"]}, True, id="or"),
        pytest.param({"AND": ["foo=='doo'", "foo=='bar'"]}, False, id="and"),
        pytest.param({"NOT": "foo=='doo'"}, True, id="not-ok"),
        pytest.param({"NOT": "foo=='bar'"}, False, id="not-nok"),
        pytest.param({}, True, id="empty"),
        pytest.param({"AND": [{"NOT": "foo=='doo'"}, "foo=='bar'"]}, True, id="nested"),
    ],
)
def test_jmespath_filter(filter_rules: Optional[Dict[str, Any] | str], result: bool) -> None:
    from bitcaster.models import Notification

    assert Notification().match_filter(rules=filter_rules, payload={"foo": "bar"}) is result


@pytest.mark.parametrize(
    "filters, result",
    [
        pytest.param({"OR": ["foo=='doo'", "foo=='bar'"]}, True, id="or"),
        pytest.param({"AND": ["foo=='doo'", "foo=='bar'"]}, False, id="and"),
        pytest.param({"NOT": "foo=='doo'"}, True, id="not-ok"),
        pytest.param({"NOT": "foo=='bar'"}, False, id="not-nok"),
        pytest.param({}, True, id="empty"),
    ],
)
def test_match_filter(filters: Optional[Dict[str, Any] | str], result: bool) -> None:
    from bitcaster.models import Notification

    assert Notification().match_filter(rules=filters, payload={"foo": "bar"}) is result
