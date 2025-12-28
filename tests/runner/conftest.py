import uuid

import pytest


@pytest.fixture
def broker():
    from bitcaster.runner.broker import broker

    broker.namespace = uuid.uuid4().hex
    return broker
