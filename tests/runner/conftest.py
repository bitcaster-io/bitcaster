import uuid

import dramatiq

import pytest


@pytest.fixture
def broker():
    from bitcaster.runner.broker import broker

    original_broker = dramatiq.get_broker()
    broker.namespace = uuid.uuid4().hex
    dramatiq.set_broker(broker)
    yield broker
    dramatiq.set_broker(original_broker)
