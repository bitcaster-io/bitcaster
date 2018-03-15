# -*- coding: utf-8 -*-
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_login(django_app, admin):
    url = reverse('admin:login')
    res = django_app.get(url)
    res.form['username'] = admin.email
    res.form['password'] = '123'
    res = res.form.submit()
    assert res.status_code == 302
    res = res.follow()
    assert res.context['user'].email == admin.email
