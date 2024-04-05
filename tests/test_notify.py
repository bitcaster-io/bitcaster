from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bitcaster.models import Application


def test_notify(application: "Application"):
    assert True
