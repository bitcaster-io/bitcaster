# -*- coding: utf-8 -*-
import pytest
from faker import Faker
from rest_framework.reverse import reverse

faker = Faker()


# @pytest.mark.django_db
# def test_user_return(django_app, application1):
#     url = reverse('index')
#     res = django_app.get(url, user=application1.organization.owner)
#
#     # get the organization dropdown
#     link = res.pyquery('.dropdown-menu a.dropdown-item.organization')[0]
#     res = res.click(href=link.get('href'))
#
#     # get the application dropdown
#     link = res.pyquery('.dropdown-menu a.dropdown-item.application')[0]
#     res = res.click(href=link.get('href'), index=1)
#
#     # goto subscriptions
#     res = res.click('Subscriptions')
#     assert res.status_code == 200
#
#     res = res.click('Channels')
#     assert res.status_code == 200
#
#     res = res.click('Events')
#     assert res.status_code == 200
#
#     res = res.click('Messages')
#     assert res.status_code == 200
