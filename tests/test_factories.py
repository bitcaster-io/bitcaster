def test_factory_event(email_channel):
    from testutils.factories import Event, EventFactory, MessageFactory

    e: "Event" = EventFactory(channels=[email_channel], messages=[MessageFactory(channel=email_channel)])
    assert e.channels.filter(pk=email_channel.pk).exists()
    assert e.messages.filter(channel__pk=email_channel.pk).exists()


def test_factory_notification(email_channel):
    from testutils.factories import (
        AssignmentFactory,
        MessageFactory,
        Notification,
        NotificationFactory,
    )

    n: "Notification" = NotificationFactory(
        distribution__recipients=[AssignmentFactory(channel=email_channel) for __ in range(4)],
        event__channels=[email_channel],
        event__messages=[MessageFactory(channel=email_channel)],
    )
    assert n.event.channels.filter(pk=email_channel.pk).exists()
    assert n.event.messages.filter(channel__pk=email_channel.pk).exists()
    assert n.distribution.recipients.count() == 4
    assert n.distribution.recipients.filter(channel=email_channel).count() == 4
