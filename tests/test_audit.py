# -*- coding: utf-8 -*-
import logging

import pytest
from django.core import mail
from django.urls import reverse
from requests_html import HTML

from bitcaster.models import AuditEvent, AuditLogEntry

pytestmark = pytest.mark.django_db


def test_audit(django_app, application1, caplog):
    EMAIL = 'user1@example.com'
    mail.outbox = []
    caplog.set_level(logging.ERROR, logger='bitcaster')

    organization = application1.organization
    owner = organization.owner
    url = reverse('org-member-invite', args=[organization.slug])
    res = django_app.get(url, user=organization.owner)

    res.form['memberships-0-email'] = EMAIL
    res.form['memberships-0-role'] = '1'  # Owner
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
    entry = AuditLogEntry.objects.filter(user=owner).latest()
    assert str(entry) == f'{owner.email} invited member user1@example.com to {organization} as Owner'
    assert organization.memberships.filter(email=EMAIL, role=1).exists()

    # get confirmation email from url
    html = HTML(html=mail.outbox[0].alternatives[0][0])
    link = html.find('a[class~=confirmation]')[0]
    url = link.attrs['href']
    res = django_app.get(url)
    res.form['password'] = 'password'
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
    entry = AuditLogEntry.objects.filter(event=AuditEvent.MEMBER_ACCEPT).latest()
    assert str(entry) == f'user1@example.com accepted invitation from {owner.email} to {organization} as Owner'
