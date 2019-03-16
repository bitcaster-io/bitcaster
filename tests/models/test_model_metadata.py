import pytest

from bitcaster.models import AgentMetaData, DispatcherMetaData

pytestmark = pytest.mark.django_db


# DispatcherMetaData
def test_dispatchermetadata():
    assert DispatcherMetaData.objects.inspect()


# AgentMetaData
def test_agentmetadata():
    assert AgentMetaData.objects.inspect()
