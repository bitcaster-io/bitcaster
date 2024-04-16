from unittest.mock import Mock

import pytest
from constance.test.unittest import override_config

from bitcaster.social.pipeline import save_to_group


@pytest.fixture()
def group(db):
    from testutils.factories import GroupFactory

    GroupFactory(name="demo")


@override_config(NEW_USER_DEFAULT_GROUP="demo")
def test_save_to_group(group, user):
    save_to_group(Mock(), user, Mock())
    assert user.groups.first().name == "demo"
