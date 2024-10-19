import pytest

from bitcaster.models import Assignment


@pytest.fixture
def fcm_url() -> str:
    return (
        "https://fcm.googleapis.com/fcm/send/dV8By98DApY:APA91bEZ-"
        "2soIyz59YPIRFUkGXhvrsDHlqyHCJj3O450hmwr8nee2FRRDPQOVkotnCI_"
        "mk41wmTWTMHCbbtiMkR8lOqqutZMAOTPHEkNpIrKCVEwD00mtPMk2zmG44E6kn22tLtKL3pM"
    )


@pytest.fixture
def push_assignment(fcm_url: str) -> "Assignment":
    from strategy_field.utils import fqn
    from testutils.factories import AssignmentFactory

    from bitcaster.webpush.dispatcher import WebPushDispatcher

    return AssignmentFactory(
        channel__config={"APPLICATION_SERVER_KEY": "aa", "private_key": "", "CLAIMS": "{}"},
        channel__dispatcher=fqn(WebPushDispatcher),
        data={
            "webpush": {
                "subscription": {
                    "endpoint": fcm_url,
                    "keys": {
                        "auth": "mp1NVQZ7lk8l991jv_IaZg",
                        "p256dh": "BF2k3PvW7s7wHlR9jvTD5vOvE4y8xaWHp73lpIE6u9dUXD0Y1J6_"
                        "fKEMW69rlvmAx--7hNMbWQ149w2g3xP8QCg",
                    },
                },
            },
        },
    )
