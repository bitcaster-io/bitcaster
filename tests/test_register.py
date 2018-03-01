# -*- coding: utf-8 -*-
import pytest
from rest_framework.reverse import reverse
from faker import Faker

from mercury.models import User, Organization
from mercury.models.organizationmember import OrganizationRole, OrganizationMember

faker = Faker()


@pytest.mark.django_db
def test_registration(django_app):
    url = reverse('user-register')
    user_email = faker.email()
    billing_email = faker.email()
    res = django_app.get(url)
    res.form['name'] = faker.name()
    res.form['email'] = user_email
    res.form['password'] = '123'
    res.form['organization'] = faker.company()
    res.form['billing_email'] = billing_email
    res.form['terms'] = True
    res = res.form.submit()
    assert res.status_code == 302, res.showbrowser()

    user = User.objects.filter(email=user_email).first()
    org = Organization.objects.filter(billing_email=billing_email).first()

    assert user
    assert org
    assert org.owner == user
    assert OrganizationMember.objects.get(organization=org,
        user__email=user_email).role == int(OrganizationRole.OWNER)
