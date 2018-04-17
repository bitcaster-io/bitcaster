# -*- coding: utf-8 -*-
import logging

import pytest
from django.urls import reverse

from bitcaster.models import User

logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_create_member(django_app, organization1):
    owner = organization1.owner

    url = reverse('org-member-register', args=[organization1.slug])
    res = django_app.get(url, user=owner.email)
    res.form['email'] = 'test@noreply.org'
    res.form['password1'] = 'Password123'
    res.form['password2'] = 'Password123'
    res = res.form.submit().follow()
    assert User.objects.get(email='test@noreply.org')


@pytest.mark.django_db
def test_create_member_fail(django_app, organization1):
    owner = organization1.owner

    url = reverse('org-member-register', args=[organization1.slug])
    res = django_app.get(url, user=owner.email)
    res.form['email'] = 'test@noreply.org'
    res.form['password1'] = 'Password123'
    res.form['password2'] = '--'
    assert res.status_code == 200
