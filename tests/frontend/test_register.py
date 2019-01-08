# -*- coding: utf-8 -*-
import pytest
from django.core import mail
from faker import Faker
from requests_html import HTML
from rest_framework.reverse import reverse

from bitcaster.db.fields import Role
from bitcaster.models import Organization, User
from bitcaster.models.organizationmember import OrganizationMember

faker = Faker()

pytestmark = pytest.mark.django_db


def test_registration(django_app, initialized):
    url = reverse('user-register')
    user_email = faker.email()
    admin_email = faker.email()
    res = django_app.get(url)
    res.form['name'] = faker.name()
    res.form['email'] = user_email
    res.form['password'] = '123'
    res.form['organization'] = faker.company()
    res.form['admin_email'] = admin_email
    res.form['terms'] = True
    res = res.form.submit()
    assert res.status_code == 302

    user = User.objects.filter(email=user_email).first()
    org = Organization.objects.filter(admin_email=admin_email).first()

    assert user
    assert org
    assert org.owner == user
    assert OrganizationMember.objects.get(organization=org,
        user__email=user_email).role == Role.OWNER

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == '[Bitcaster] Confirm Email'
    # get confirmation email from url
    html = HTML(html=mail.outbox[0].alternatives[0][0])
    link = html.find('a[class~=confirmation]')[0]
    url = link.attrs['href']
    res = django_app.get(url)
    # assert 'Create application' in str(res.content)
