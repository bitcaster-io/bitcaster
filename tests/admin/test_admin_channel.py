from smtplib import SMTP
from unittest.mock import Mock, patch

import pytest
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.db.models.options import Options
from django.urls import reverse
from django_webtest import DjangoTestApp
from strategy_field.utils import fqn

from bitcaster.models import Channel


@pytest.fixture()
def app(django_app_factory, db):
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture()
def gmail_channel(db):
    from testutils.factories.channel import ChannelFactory

    from bitcaster.dispatchers import GMmailDispatcher

    return ChannelFactory(dispatcher=fqn(GMmailDispatcher), config={"username": "username", "password": "password"})


def test_configure(app: DjangoTestApp, gmail_channel):
    opts: Options = Channel._meta
    url = reverse(admin_urlname(opts, "configure"), args=[gmail_channel.pk])
    res = app.get(url)
    assert res.status_code == 200

    res = app.post(url, {"username": "username", "password": "password"})
    assert res.status_code == 302


def test_test(app: DjangoTestApp, gmail_channel):
    opts: Options = Channel._meta
    url = reverse(admin_urlname(opts, "test"), args=[gmail_channel.pk])
    res = app.get(url)
    assert res.status_code == 200
    with patch("smtplib.SMTP", autospec=True) as mock:
        res = app.post(url, {"recipient": "recipient", "subject": "subject", "message": "message"})
    assert res.status_code == 200

    mock.assert_called()
    s: Mock[SMTP] = mock.return_value
    s.login.assert_called()
    s.starttls.assert_called()
    s.sendmail.assert_called()
