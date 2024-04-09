import pytest

from bitcaster.models import Subscription

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
def test_simple_filter(
    statement,
):
    # now we test a non-matching filter
    result = Subscription.match_filter_impl(
        {"{statement}": ["people[?general.id==`999`].general | [0]"]}, EXAMPLE_PAYLOAD
    )

    assert result is False


def test_plain_filter():
    # now we test a matching filter
    result = Subscription.match_filter_impl("status == 'terminated: completed'", {"status": "terminated: completed"})

    assert result is True
