# -*- coding: utf-8 -*-

import pytest


@pytest.fixture
def api_client(user1, db):
    from tests_utils import client_factory
    return client_factory(user1)
