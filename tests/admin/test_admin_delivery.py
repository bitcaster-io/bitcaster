from typing import TYPE_CHECKING

import pytest
from testutils.factories import (
    AssignmentFactory,
    ChannelFactory,
    EventFactory,
    MessageTemplateFactory,
    NotificationFactory,
    OccurrenceFactory,
)
from testutils.perms import user_grant_permissions

from django.urls import reverse
from django_webtest import DjangoTestApp
from django_webtest.pytest_plugin import MixinWithInstanceVariables

if TYPE_CHECKING:
    from webtest.response import TestResponse

    from bitcaster.models import User

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def app_for_admin(django_app_factory: MixinWithInstanceVariables, admin_user: "User") -> DjangoTestApp:
    django_app: DjangoTestApp = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture
def delivery(app_for_admin):
    from bitcaster.models import Delivery

    ch = ChannelFactory.create()
    event = EventFactory.create(channels=[ch])
    asm = AssignmentFactory.create(channel=ch)
    n = NotificationFactory.create(distribution__recipients=[asm], event=event)
    MessageTemplateFactory.create(event=event, channel=ch)
    occurrence = OccurrenceFactory.create(event=n.event, status="NEW")
    return Delivery.objects.create(
        occurrence=occurrence,
        assignment=asm,
        notification=n,
        channel=ch,
    )


def test_delivery_changelist_invalid_occurrence(app_for_admin: DjangoTestApp) -> None:
    """Line 39: invalid occurrence_id should not crash."""
    url = reverse("admin:bitcaster_delivery_changelist")
    res: "TestResponse" = app_for_admin.get(f"{url}?occurrence__exact=invalid")
    assert res.status_code == 302
    res = res.follow()
    assert res.status_code == 200


def test_delivery_changelist_nonexistent_occurrence(app_for_admin: DjangoTestApp) -> None:
    """Line 39: nonexistent occurrence_id should not crash."""
    url = reverse("admin:bitcaster_delivery_changelist")
    res: "TestResponse" = app_for_admin.get(f"{url}?occurrence__exact=99999")
    assert res.status_code == 200


def test_delivery_fields_without_read_data_perm(django_app_factory: MixinWithInstanceVariables, delivery, db) -> None:
    """Line 46: users without read_data_delivery permission should not see 'data' field."""
    from testutils.factories import UserFactory

    user = UserFactory(is_staff=True, is_superuser=False)
    django_app: DjangoTestApp = django_app_factory(csrf_checks=False)
    django_app.set_user(user)
    with user_grant_permissions(user, ["bitcaster.view_delivery"]):
        url = reverse("admin:bitcaster_delivery_change", args=[delivery.pk])
        res: "TestResponse" = django_app.get(url)
    assert res.status_code == 200
    assert "field-data" not in res.text


def test_delivery_fields_with_read_data_perm(app_for_admin: DjangoTestApp, delivery) -> None:
    """Line 46: admin users with read_data_delivery permission should see 'data' field."""
    url = reverse("admin:bitcaster_delivery_change", args=[delivery.pk])
    res: "TestResponse" = app_for_admin.get(url)
    assert res.status_code == 200
