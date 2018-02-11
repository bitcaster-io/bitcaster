import pytest
from rest_framework.reverse import reverse

from mercury.dispatchers import dispatcher_registry


@pytest.mark.django_db
def test_list_dispatcher(api_client):
    url = reverse('api:dispatcher-list')
    response = api_client.get(url, format='json')
    res = response.json()
    assert len(res) == len(dispatcher_registry)
