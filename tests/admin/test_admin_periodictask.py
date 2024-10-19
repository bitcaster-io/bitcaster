from typing import TYPE_CHECKING, Any

import pytest
from django.urls import reverse
from django_webtest import DjangoTestApp
from django_webtest.pytest_plugin import MixinWithInstanceVariables

if TYPE_CHECKING:
    from bitcaster.models import Monitor


@pytest.fixture()
def app(django_app_factory: MixinWithInstanceVariables, db: Any) -> DjangoTestApp:
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_run(app: DjangoTestApp, monitor: "Monitor") -> None:
    url = reverse(
        "admin:django_celery_beat_periodictask_change", args=[monitor.schedule.pk]  # type: ignore[union-attr]
    )
    res = app.get(url)
    res = res.click("Run")
    assert res.status_code == 302
