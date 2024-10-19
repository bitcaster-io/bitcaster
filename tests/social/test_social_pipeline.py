from typing import Any
from unittest.mock import Mock

import pytest
from constance.test.unittest import override_config
from django.contrib.auth.models import Group

from bitcaster.models import User
from bitcaster.social.pipeline import save_to_group


@pytest.fixture()
def group(db: Any) -> None:
    from testutils.factories import GroupFactory

    GroupFactory(name="demo")


@override_config(NEW_USER_DEFAULT_GROUP="demo")  # type: ignore[misc]
def test_save_to_group(group: "Group", user: "User") -> None:
    save_to_group(Mock(), user)
    assert user.groups.first().name == "demo"
    assert save_to_group(Mock(), None) == {}
