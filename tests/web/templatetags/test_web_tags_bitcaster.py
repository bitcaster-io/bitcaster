from bitcaster.web.templatetags.bitcaster import recipients


def test_bitcaster_recipients(occurrence):
    assert recipients({"address": ""}, occurrence)


def test_bitcaster_recipients_notification(occurrence, notification):
    assert recipients({"address": ""}, occurrence, notification=notification)


def test_bitcaster_recipients_channel(occurrence, channel):
    assert recipients({"address": ""}, occurrence, channel=channel)
