# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

import pytest
from rest_framework.reverse import reverse

from mercury.models import Application
from mercury.utils.tests.factories import client_factory

logger = logging.getLogger(__name__)


# READ_EXPECTED_STATUSES = [("superuser", 200),
#                           ("owner", 200),
#                           ("account", 200),
# ("authorized", 404),  # no auth
# ("user", 404),
# ("anonymous", 403)]
# ROLES = [k[0] for k in READ_EXPECTED_STATUSES]
#

#
# WRITE_EXPECTED_STATUSES = [("superuser", 200),
#                            ("owner", 200),
#                            # ("account", 403),
#                            ("authorized", 404),  # no auth
#                            ("user", 404),
#                            ("anonymous", 403)]
#
# ADDEVENT_EXPECTED_STATUSES = [("superuser", 201),
#                               ("owner", 201),
#                               # ("account", 403),
#                               ("authorized", 403),  # no auth
#                               ("user", 403),
#                               ("anonymous", 403)]
#
# EDITEVENT_EXPECTED_STATUSES = [("superuser", 200),
#                                ("owner", 200),
#                                # ("account", 403),
#                                ("authorized", 403),  # no auth
#                                ("user", 403),
#                                ("anonymous", 403)]

def test_application_list(organization1, application2):
    url = reverse('api:application-list')
    client = client_factory(organization1.owner)
    res = client.get(url)
    assert res.status_code == 200, str(res.content)
    assert len(res.json()) == 1


def test_application_create(organization1):
    url = reverse('api:application-list')
    client = client_factory(organization1.owner)
    res = client.post(url, {'name': 'App1',
                            'organization': organization1})
    assert res.status_code == 201, str(res.content)
    app = Application.objects.get(pk=res.json()['id'])
    assert app.tokens.first()


def test_application_edit(application1):
    url = reverse('api:application-detail', args=[application1.pk])
    client = client_factory(application1.organization.owner)
    res = client.put(url, {'name': 'App1-1'})
    assert res.status_code == 200, str(res.content)
    app = Application.objects.get(pk=res.json()['id'])
    assert app.tokens.count() == 1


def test_application_delete(application1):
    url = reverse('api:application-detail', args=[application1.pk])
    client = client_factory(application1.organization.owner)
    res = client.delete(url)
    assert res.status_code == 204, str(res.content)
    with pytest.raises(Application.DoesNotExist):
        application1.refresh_from_db()


def test_application_generate_token(application1):
    url = reverse('api:application-generate-token', args=[application1.pk])
    client = client_factory(application1.organization.owner)
    res = client.post(url)
    application1.refresh_from_db()
    assert res.status_code == 201, str(res.content)
    token = res.json()['token']
    assert application1.tokens.filter(token=token).exists()


def test_application_add_maintainer(application1, user2):
    url = reverse('api:application-add-maintainer', args=[application1.pk])
    api_client = client_factory(application1.organization.owner)
    response = api_client.post(url, {'email': user2.email})
    assert response.status_code == 200, str(response.content)
    assert user2 in application1.maintainers.all()


def test_application_maintainer_can_edit(application1, maintaner1):
    url = reverse('api:application-detail', args=[application1.pk])
    client = client_factory(maintaner1)
    res = client.put(url, {'name': 'App1-1'})
    assert res.status_code == 200, str(res.content)
    app = Application.objects.get(pk=res.json()['id'])
    assert app.tokens.count() == 1


###

def test_application_list1(application1, application2):
    """ user can only list 'owned' application """
    url = reverse('api:application-list')
    client = client_factory(application1.organization.owner)
    res = client.get(url)
    assert res.status_code == 200, str(res.content)
    results = res.json()
    assert len(results) == 1

# def test_application_add_maintainer1(application1):
#     """ add_maintainer accepts email addresses """
#     url = reverse('api:application-add-maintainer', args=[application1.pk])
#     api_client = client_factory(application1.organization.owner)
#     response = api_client.post(url, {'email': '---'})
#     assert response.status_code == 400, str(response.content)


#
# def get_user_for_app(role, application1):
#     return {'superuser': AdminFactory(),
#             "anonymous": get_anonymous_user(),
#             "owner": application1.owner,
#             # "account": application1.account,
#             "authorized": UserFactory(permissions=['mercury.view_application']),
#             "user": UserFactory()}[role]
#
#
# @pytest.mark.parametrize("args", READ_EXPECTED_STATUSES, ids=ROLES)
# @pytest.mark.django_db
# def test_get_record_check_user(application1, args):
#     """ check user access permission"""
#     url = reverse('api:application-detail', [application1.pk])
#     role, code = args
#     requestor = get_user_for_app(role, application1)
#     api_client = client_factory(requestor, force=True)
#
#     response = api_client.get(url, format='json')
#     assert response.status_code == code, str(response.content)
#
#
# @pytest.mark.django_db
# def test_get_record_by_name(application1):
#     """ allow retrieve record by pk/name"""
#     url = reverse('api:application-detail', [application1.name])
#     api_client = client_factory(application1.owner)
#     response = api_client.get(url, format='json')
#     assert response.status_code == 200, str(response.content)
#
#
# @pytest.mark.django_db
# def test_list(application1):
#     api_client = client_factory(application1.owner)
#     url = reverse('api:application-list')
#     response = api_client.get(url, format='json')
#     res = response.json()
#     assert len(res) == Application.objects.count()
#
#
# # @pytest.mark.django_db
# # def test_list_not_allowed_to_application_account(application1):
# #     url = reverse('api:application-list')
# #     api_client = client_factory(application1.account)
# #     response = api_client.get(url, format='json')
# #     assert response.status_code == 403, str(response.content)
#
#
# @pytest.mark.django_db
# def test_create(api_client):
#     url = reverse('api:application-list')
#     api_client2 = client_factory(None, force=True)
#     response = api_client2.post(url, format='json')
#     assert response.status_code == 403, str(response.content)
#
#     with user_grant_permissions(api_client.handler._force_user, ['mercury.add_application']):
#         response = api_client.post(url, {'name': '',
#                                          'timezone': 'Europe/Rome'}, format='json')
#         assert response.status_code == 400
#
#         response = api_client.post(url, {'name': 'app1',
#                                          'password': 123,
#                                          'timezone': 'Europe/Rome'}, format='json')
#     assert response.status_code == 201, str(response.content)
#     app = Application.objects.filter(name='app1').first()
#     assert app
#     assert app.timezone == pytz.timezone('Europe/Rome')
#     assert app.owner == api_client.handler._force_user
#
#
# @pytest.mark.django_db
# def test_create_with_owner(api_client):
#     url = reverse('api:application-list')
#     response = api_client.post(url, {'name': 'app1',
#                                      'password': 123,
#                                      'timezone': 'Europe/Rome'}, format='json')
#     assert response.status_code == 201, str(response.content)
#     app = Application.objects.filter(name='app1').first()
#     assert app.owner == api_client.handler._force_user
#
#
# @pytest.mark.django_db
# def test_add_maintainer_missed_argument(application1):
#     url = reverse('api:application-add-maintainer', args=[application1.pk])
#     api_client = client_factory(application1.owner)
#     response = api_client.post(url, {'username': ''}, format='json')
#     assert response.status_code == 400, str(response.content)
#
#
# @pytest.mark.django_db
# def test_add_maintainer_wrong_user(application1):
#     url = reverse('api:application-add-maintainer', args=[application1.pk])
#     api_client = client_factory(application1.owner)
#     response = api_client.post(url, {'username': '--'}, format='json')
#     assert response.status_code == 400, str(response.content)
#
#
# @pytest.mark.parametrize("args", WRITE_EXPECTED_STATUSES, ids=ROLES)
# @pytest.mark.django_db
# def test_reset_password(application1, args):
#     url = reverse('api:application-reset-password', args=[application1.pk])
#     role, code = args
#     requestor = get_user_for_app(role, application1)
#     api_client = client_factory(requestor, force=True)
#
#     response = api_client.post(url, format='json')
#
#     assert response.status_code == code, str(response.content)
#
# #
# # @pytest.mark.django_db
# # def test_add_event(channel1):
# #     application = channel1.application
# #     url = reverse(r'api:application-event-list', args=[application.pk])
# #     api_client = client_factory(application.owner)
# #     response = api_client.post(url, {'name': 'Event1',
# #                                      'allowed_channels': [channel1.name],
# #                                      'template': 'template1',
# #                                      'subject': 'subject1'}, format='json')
# #
# #     assert response.status_code == 201, str(response.content)
#
#
# # @pytest.mark.django_db
# # def test_add_event_check_application(channel1, channel2):
# #     """application can only add"""
# #     application = channel1.application
# #     url = reverse(r'api:application-event-list', args=[application.pk])
# #     api_client = client_factory(application.owner)
# #     response = api_client.post(url, {'name': 'Event1',
# #                                      'allowed_channels': [channel2.name],
# #                                      'template': 'template1',
# #                                      'subject': 'subject1'}, format='json')
# #
# #     assert response.status_code == 400, str(response.content)
#
# #
# # @pytest.mark.parametrize("args", EDITEVENT_EXPECTED_STATUSES, ids=ROLES)
# # @pytest.mark.django_db
# # def test_edit_event(application1, event, args):
# #     url = reverse(r'api:application-events', args=[application1.pk, event.pk])
# #     role, code = args
# #     requestor = get_user_for_app(role, application1)
# #     api_client = client_factory(requestor)
# #     response = api_client.put(url, {'name': 'Event1',
# #                                     'allowed_channels': [event.allowed_channels.first().name],
# #                                     'template': 'template1',
# #                                     'subject': 'subject1'}, format='json')
# #
# #     assert response.status_code == code, str(response.content)
# #
# #
# # @pytest.mark.parametrize("args", EDITEVENT_EXPECTED_STATUSES, ids=ROLES)
# # @pytest.mark.django_db
# # def test_patch_event(event, args):
# #     url = reverse(r'api:application-event', args=[event.application1.pk, event.pk])
# #     role, code = args
# #     requestor = get_user_for_app(role, event.application1)
# #     api_client = client_factory(requestor)
# #     response = api_client.patch(url, {'name': 'Event1.1'}, format='json')
# #
# #     assert response.status_code == code, str(response.content)
