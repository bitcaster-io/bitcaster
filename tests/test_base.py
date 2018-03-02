# -*- coding: utf-8 -*-
from django.urls import reverse


def test_login(django_app, admin):
    url = reverse('admin:login')
    res = django_app.get(url)
    res.form['username'] = admin.email
    res.form['password'] = '123'
    res = res.form.submit()
    assert res.status_code == 302
    res = res.follow()
    assert res.context['user'].email == admin.email
