from typing import TYPE_CHECKING, Any, Iterable

import pytest
from django.contrib.admin import ModelAdmin
from django.contrib.admin.sites import site
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.db.models import Model
from django.db.models.options import Options
from django.urls import reverse
from django_regex.utils import RegexList as _RegexList
from django_webtest import DjangoTestApp
from testutils.factories.base import AutoRegisterModelFactory

from bitcaster.models.mixins import LockMixin

if TYPE_CHECKING:
    from django_webtest.pytest_plugin import MixinWithInstanceVariables
    from pytest import FixtureRequest, Metafunc
    from pytest_django.fixtures import SettingsWrapper
    from responses import RequestsMock


pytestmark = [pytest.mark.admin, pytest.mark.smoke, pytest.mark.django_db]


class RegexList(_RegexList):  # type: ignore[misc]
    def extend(self, __iterable: "Iterable[Any]") -> None:
        for e in __iterable:
            self.append(e)


def pytest_generate_tests(metafunc: "Metafunc") -> None:
    import django

    from bitcaster.admin.mixins import LockMixinAdmin

    markers = metafunc.definition.own_markers
    excluded_models = RegexList()
    if "skip_models" in [m.name for m in markers]:
        skip_rule = list(filter(lambda m: m.name == "skip_models", markers))[0]
        excluded_models.extend(skip_rule.args)
    django.setup()
    if "model_admin" in metafunc.fixturenames:
        m = []
        ids = []
        for model, admin in site._registry.items():
            if isinstance(admin, LockMixinAdmin):
                name = model._meta.object_name
                full_name = f"{model._meta.app_label}.{name}"
                if not (full_name in excluded_models):
                    m.append(admin)
                    ids.append(f"{admin.__class__.__name__}:{full_name}")
        metafunc.parametrize("model_admin", m, ids=ids)


@pytest.fixture()
def record(db: Any, request: "FixtureRequest") -> Model:
    from testutils.factories import get_factory_for_model

    # TIPS: database access is forbidden in pytest_generate_tests
    model_admin = request.getfixturevalue("model_admin")
    instance: Model = model_admin.model.objects.first()
    if not instance:
        # full_name = f"{model_admin.model._meta.app_label}.{model_admin.model._meta.object_name}"
        factory: type[AutoRegisterModelFactory[Any]] = get_factory_for_model(model_admin.model)
        try:
            instance = factory()
        except Exception as e:
            raise Exception(f"Error creating fixture for {factory}") from e
    return instance


@pytest.fixture()
def app(
    django_app_factory: "MixinWithInstanceVariables", mocked_responses: "RequestsMock", settings: "SettingsWrapper"
) -> DjangoTestApp:
    from testutils.factories import SuperUserFactory

    settings.FLAGS = {"BETA_PREVIEW_LOCKING": [("boolean", True)]}

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_admin_lock(app: "DjangoTestApp", model_admin: ModelAdmin[LockMixin], record: LockMixin) -> None:
    opts: Options[LockMixin] = model_admin.model._meta
    url = reverse(admin_urlname(opts, "change"), args=[record.pk])  # type: ignore[arg-type]

    res = app.get(url)
    assert str(opts.app_config.verbose_name) in res.body.decode()
    res = res.click(".Lock$")
    assert res.status_code == 200
    res = res.forms["lock-form"].submit()
    assert res.status_code == 302
    record.refresh_from_db()
    assert record.locked


def test_admin_unlock(app: DjangoTestApp, model_admin: ModelAdmin[LockMixin], record: LockMixin) -> None:
    opts: Options[LockMixin] = model_admin.model._meta
    url = reverse(admin_urlname(opts, "change"), args=[record.pk])  # type: ignore[arg-type]
    record.locked = True
    record.save()

    res = app.get(url)
    assert str(opts.app_config.verbose_name) in res.body.decode()
    res = res.click(".Unlock$")
    assert res.status_code == 200
    res = res.forms["lock-form"].submit()
    assert res.status_code == 302
    record.refresh_from_db()
    assert not record.locked


# @pytest.mark.skip_models("constance.Config", "advanced_filters.AdvancedFilter")
# def test_admin_lock(app, model_admin, record):
#     opts: Options = model_admin.model._meta
#     url = reverse(admin_urlname(opts, "change"), args=[record.pk])
#
#     res = app.get(url)
#     assert str(opts.app_config.verbose_name) in res.body.decode()
#     res.click("lock")
#     assert res.status_code == 200
#     res.click("lock")
#     assert res.status_code == 302
#     assert record.locked
