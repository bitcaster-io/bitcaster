from bitcaster.utils.crontab import human_readable


def test_human_readable():
    assert human_readable("* */5 * * * *") == "Every second, every 5 minutes"
    assert human_readable("*") == "*"
