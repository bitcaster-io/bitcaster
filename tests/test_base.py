# -*- coding: utf-8 -*-
from django.urls import reverse


def test_login(django_app, admin_user):
    url = reverse('admin:login')
    res = django_app.get(url)
    res.form['username'] = 'admin'
    res.form['password'] = 'password'
    res = res.form.submit()
    assert res.status_code == 302
    res = res.follow()
    assert res.context['user'].username == 'admin'
