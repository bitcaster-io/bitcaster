import pytest
from strategy_field.utils import fqn

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


def test_sys(mail_payload, mailoutbox):
    from bitcaster.dispatchers import SystemDispatcher
    from bitcaster.models import Application, Channel

    SystemDispatcher(
        Channel(
            application=Application(from_email="from@example.com", subject_prefix="[sys] "),
            dispatcher=fqn(SystemDispatcher),
        )
    ).send("test@example.com", mail_payload)
    assert len(mailoutbox) == 1
    assert mailoutbox[0].subject == "[sys] subject"
