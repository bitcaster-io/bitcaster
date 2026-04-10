import pytest

from bitcaster.utils.crontab import human_readable


def test_human_readable():
    assert human_readable("* */5 * * * *") == "Every second, every 5 minutes"
    assert human_readable("*") == "*"


@pytest.mark.parametrize(
    "cron",
    [
        "invalid",
        "",
        "1 2 3",
        "A B C D E",
    ],
)
def test_human_readable_invalid(cron):
    assert human_readable(cron) == cron
