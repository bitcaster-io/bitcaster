# -*- coding: utf-8 -*-

import pytest
from django.urls import reverse
from tests_utils import UserFactory

# @pytest.mark.django_db
# def test_list(api_client):
#     url = reverse('api:user-list')
#     response = api_client.get(url, format='json')
#     assert response.status_code == 200
#     assert len(response.json()) == 1
#
#     with user_grant_permissions(api_client.handler._force_user, ['mercury.view_user']):
#         response = api_client.get(url, format='json')
#     res = response.json()
#     assert len(res) == User.objects.count(), res


# @pytest.mark.django_db
# def test_create(api_client):
#     url = reverse('api:user-list')
#     response = api_client.post(url, format='json')
#     assert response.status_code == 403
#     with user_grant_permissions(api_client.handler._force_user, ['mercury.add_user']):
#         response = api_client.post(url, {'username': 'abc',
#                                          'password': '123'}, format='json')
#     assert response.status_code == 201
#     assert User.objects.filter(username='abc').exists()


@pytest.mark.django_db
def test_change_password(api_client, user1):
    url = reverse('api:user-change-password', args=[api_client.handler._force_user.pk])
    hacked = reverse('api:user-change-password', args=[UserFactory().pk])

    # check fields
    response = api_client.post(url, format='json')
    assert response.status_code == 400, str(response.content)

    # check password match
    response = api_client.post(url, {'password1': '123',
                                     'password2': 'xxx'}, format='json')
    assert response.status_code == 400, str(response.content)

    # user can only change his password
    response = api_client.post(hacked, {'password1': '123',
                                        'password2': 'xxx'}, format='json')
    assert response.status_code == 404, str(response.content)

    # success call
    response = api_client.post(url, {'password1': '123',
                                     'password2': '123'}, format='json')
    assert response.status_code == 200, str(response.content)
