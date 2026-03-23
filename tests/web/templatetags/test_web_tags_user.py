from typing import TYPE_CHECKING

import pytest
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from testutils.factories import UserFactory

from bitcaster.web.templatetags.user import user_date, user_datetime

if TYPE_CHECKING:
    from bitcaster.models import User


@pytest.mark.parametrize("dt, expected", [(None, False), (timezone.now(), True)])
@pytest.mark.parametrize("user", ["user", AnonymousUser()])
def test_user_date(user: "User", dt, rf, expected) -> None:
    request = rf.get("/")
    if isinstance(user, str):
        user = UserFactory.create()
    request.user = user
    assert bool(user_date({"request": request}, dt)) is expected


@pytest.mark.parametrize("dt, expected", [(None, False), (timezone.now(), True)])
@pytest.mark.parametrize("user", ["user", AnonymousUser()])
def test_user_datetime(user: "User", dt, rf, expected) -> None:
    request = rf.get("/")
    if isinstance(user, str):
        user = UserFactory.create()
    request.user = user
    assert bool(user_datetime({"request": request}, dt)) is expected
