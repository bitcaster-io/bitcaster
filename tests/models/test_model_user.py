from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from bitcaster.models import Address, User


def test_user(db: Any) -> None:
    from testutils.factories import UserFactory

    u: "User" = UserFactory()
    addr: "Address" = u.addresses.create(value="test@example.com")

    assert list(u.addresses.all()) == [addr]
