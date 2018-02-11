import pytest
import pytz
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_list_detectors(api_client):
    url = reverse('api:timezone-list')
    response = api_client.get(url, format='json')
    res = response.json()
    assert len(res) == len(pytz.all_timezones)
