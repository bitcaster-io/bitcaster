import pytest

from bitcaster.utils.address import is_email, is_phonenumber


@pytest.mark.parametrize("value, result", [("user@email.com", True), ("aaa", False), (123, False), ("a@b@", False)])
def test_is_email(value, result: bool):
    assert is_email(value) is result


@pytest.mark.parametrize(
    "value, result",
    [
        ("aa", False),
        ("123", False),
        ("+12299088128", True),
        ("+1 (233) 999-6397", True),
    ],
)
def test_is_phonenumber(value, result):
    assert is_phonenumber(value) is result
