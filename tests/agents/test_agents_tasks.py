from unittest import mock

import pytest

from bitcaster.agents import EmailAgent
from bitcaster.agents.tasks import check_all
from bitcaster.utils.reflect import fqn

pytestmark = pytest.mark.django_db


@pytest.mark.plugin
def test_check_all(monitor1):
    with mock.patch(fqn(EmailAgent)):
        assert check_all()
