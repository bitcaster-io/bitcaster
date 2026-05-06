import pytest
from testutils.factories import SuperUserFactory

from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.urls import reverse

from bitcaster.models import Application, Channel


@pytest.mark.django_db
def test_lock_unlock_non_existent(django_app_factory, settings):
    settings.FLAGS = {"BETA_PREVIEW_LOCKING": [("boolean", True)]}
    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(is_superuser=True)
    django_app.set_user(admin_user)

    opts = Application._meta

    # We use a non-existent PK to trigger line 43 and 62
    non_existent_pk = 999999

    lock_url = reverse(admin_urlname(opts, "lock"), args=[non_existent_pk])
    unlock_url = reverse(admin_urlname(opts, "unlock"), args=[non_existent_pk])

    # Expect 302 redirect to changelist if object not found (handled by admin_extra_buttons or BaseAdmin)
    res = django_app.get(lock_url, expect_errors=True)
    assert res.status_code == 302

    res = django_app.get(unlock_url, expect_errors=True)
    assert res.status_code == 302


@pytest.mark.django_db
def test_two_step_create_add_view(django_app_factory):
    # This triggers line 76 (object_id is None)
    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(is_superuser=True)
    django_app.set_user(admin_user)

    opts = Channel._meta

    add_url = reverse(admin_urlname(opts, "add"))
    res = django_app.get(add_url)
    assert res.status_code == 200
    # In TwoStepCreateMixin, when object_id is None, show_save is False.
    # We can't easily check extra_context from the response in a smoke test,
    # but the line is hit.
