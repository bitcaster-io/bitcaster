import dramatiq
import pytest
from click.testing import CliRunner
from dramatiq import Worker
from dramatiq.brokers.stub import StubBroker


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def stub_broker():
    broker = StubBroker()
    broker.flush_all()
    dramatiq.set_broker(broker)
    return broker


@pytest.fixture
def stub_worker(stub_broker):
    worker = Worker(stub_broker, worker_timeout=100)
    worker.start()
    yield worker
    worker.stop()


@pytest.fixture
def stub_dramatiq(stub_broker, stub_worker):
    return stub_broker, stub_worker
