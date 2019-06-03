import pytest

# @pytest.mark.django_db
# def test_process_event_no_messages(subscription1, occurence1):
#     channel = subscription1.channel
#     channel.messages.all().delete()
#     event = subscription1.event
#     with pytest.raises(ObjectDoesNotExist):
#         assert process_channel(channel.pk, event.pk, occurence1.pk, {})
from bitcaster.tasks.event import trigger_event

# @pytest.mark.django_db
# def test_process_event(subscription1, occurence1):
#     channel = subscription1.channel
#     event = subscription1.event
#     assert process_channel(channel.pk, event.pk, occurence1.pk, {})

#
# @pytest.mark.django_db
# def test_process_event_errors_threshold(subscription1):
#     channel = subscription1.channel
#     channel.errors_threshold = 0
#     event = subscription1.event
#     with pytest.raises(MaxChannelError):
#         with mock.patch('bitcaster.models.Notification.log'):
#             H = fqn(channel.handler)
#             H.emit =  MagicMock(side_effect=Mock(side_effect=Exception))
#             # with mock.patch(,
#             #                 emit=):
#             assert process_channel(channel.pk, event.pk, {})
#     assert not channel.enabled


@pytest.mark.django_db
def test_emit_event(occurence1):
    assert trigger_event(occurence1.pk, {})


@pytest.mark.django_db
def test_acknowledge():
    pass
