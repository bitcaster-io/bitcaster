from typing import TYPE_CHECKING, Any, Iterable, Mapping, Optional
from unittest.mock import Mock

import pytest
from admin_extra_buttons.handlers import ButtonHandler, ChoiceHandler
from admin_extra_buttons.mixins import ExtraButtonsMixin
from django.contrib.admin.sites import site
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.db.models import Model
from django.db.models.options import Options
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_regex.utils import RegexList as _RegexList
from pytest_django.fixtures import SettingsWrapper
from responses import RequestsMock
from testutils.factories.base import AutoRegisterModelFactory
from testutils.factories.user import SuperUserFactory

if TYPE_CHECKING:
    from django.contrib.admin import ModelAdmin
    from django_webtest import DjangoTestApp, DjangoWebtestResponse
    from django_webtest.pytest_plugin import MixinWithInstanceVariables
    from pytest import FixtureRequest, Metafunc, MonkeyPatch

pytestmark = [pytest.mark.admin, pytest.mark.smoke, pytest.mark.django_db]


class RegexList(_RegexList):  # type: ignore[misc]
    def extend(self, __iterable: "Iterable[Any]") -> None:
        for e in __iterable:
            self.append(e)


GLOBAL_EXCLUDED_MODELS = RegexList(
    [
        r"django_celery_beat\.ClockedSchedule",
        r"contenttypes\.ContentType",
        r"webpush\.BrowserAdmin",
        "authtoken",
        "social_django",
        "depot",
    ]
)

GLOBAL_EXCLUDED_BUTTONS = RegexList(
    [
        r"social.SocialProviderAdmin:test",
        r"bitcaster.*:lock",
        r"bitcaster.*:unlock",
    ]
)

KWARGS: Mapping[str, Any] = {}


def reverse_model_admin(model_admin: "ModelAdmin[Model]", op: str, args: Optional[list[Any]] = None) -> str:
    if args:
        return reverse(admin_urlname(model_admin.model._meta, mark_safe(op)), args=args)
    else:
        return reverse(admin_urlname(model_admin.model._meta, mark_safe(op)))


def log_submit_error(res: "DjangoWebtestResponse") -> str:
    try:
        return f"Submit failed with: {repr(res.context['form'].errors)}"
    except KeyError:
        return "Submit failed"


def pytest_generate_tests(metafunc: "Metafunc") -> None:  # noqa
    import django

    ids: list[str]

    markers = metafunc.definition.own_markers
    excluded_models = RegexList(GLOBAL_EXCLUDED_MODELS)
    excluded_buttons = RegexList(GLOBAL_EXCLUDED_BUTTONS)
    if "skip_models" in [m.name for m in markers]:
        skip_rule = list(filter(lambda m: m.name == "skip_models", markers))[0]
        excluded_models.extend(skip_rule.args)
    if "skip_buttons" in [m.name for m in markers]:
        skip_rule = list(filter(lambda m: m.name == "skip_buttons", markers))[0]
        excluded_buttons.extend(skip_rule.args)
    django.setup()
    if "button_handler" in metafunc.fixturenames:
        m1: list[tuple[ModelAdmin[ExtraButtonsMixin], ButtonHandler]] = []
        ids = []
        for model, admin in site._registry.items():
            if hasattr(admin, "extra_button_handlers"):
                name = model._meta.object_name
                assert admin.urls  # we need to force this call
                # admin.get_urls()  # we need to force this call
                buttons = admin.extra_button_handlers.values()
                full_name = f"{model._meta.app_label}.{name}"
                admin_name = f"{model._meta.app_label}.{admin.__class__.__name__}"
                if not (full_name in excluded_models):
                    for btn in buttons:
                        tid = f"{admin_name}:{btn.name}"
                        if tid not in excluded_buttons:
                            m1.append((admin, btn))
                            ids.append(tid)
        metafunc.parametrize("model_admin,button_handler", m1, ids=ids)
    elif "app_label" in metafunc.fixturenames:
        m: dict[str, int] = {}
        for model, admin in site._registry.items():
            m[model._meta.app_label] = 1
        metafunc.parametrize("app_label", m.keys(), ids=m.keys())
    elif "model_admin" in metafunc.fixturenames:
        m2: list[ModelAdmin[Model]] = []
        ids = []
        for model, admin in site._registry.items():
            name = model._meta.object_name
            full_name = f"{model._meta.app_label}.{name}"
            if not (full_name in excluded_models):
                m2.append(admin)
                ids.append(f"{admin.__class__.__name__}:{full_name}")
        metafunc.parametrize("model_admin", m2, ids=ids)


@pytest.fixture()
def record(db: Any, request: "FixtureRequest") -> Model:
    from testutils.factories import get_factory_for_model

    model_admin = request.getfixturevalue("model_admin")
    instance: Model = model_admin.model.objects.first()
    if not instance:
        full_name = f"{model_admin.model._meta.app_label}.{model_admin.model._meta.object_name}"
        factory: type[AutoRegisterModelFactory[Any]] = get_factory_for_model(model_admin.model)
        try:
            instance = factory(**KWARGS.get(full_name, {}))
        except Exception as e:
            raise Exception(f"Error creating fixture for {factory} using {KWARGS}") from e
    return instance


@pytest.fixture()
def app(
    django_app_factory: "MixinWithInstanceVariables", mocked_responses: "RequestsMock", settings: SettingsWrapper
) -> "DjangoTestApp":
    settings.FLAGS = {"OLD_STYLE_UI": [("boolean", True)]}
    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_app_list(app: "DjangoTestApp", app_label: str) -> None:
    url = reverse("admin:app_list", args=[app_label])
    res = app.get(url)
    assert res.status_code == 200


@pytest.mark.skip_models("constance.Config")
def test_admin_changelist(app: "DjangoTestApp", model_admin: "ModelAdmin[Model]", record: Model) -> None:
    url = reverse_model_admin(model_admin, "changelist")
    opts: Options[Model] = model_admin.model._meta
    res = app.get(url)
    assert res.status_code == 200, res.location
    assert str(opts.app_config.verbose_name) in str(res.content)
    if model_admin.has_change_permission(Mock(user=app._user)):
        assert f"/{record.pk}/change/" in res.body.decode()


def show_error(res: Any) -> tuple[str]:
    errors = []
    for k, v in dict(res.context["adminform"].form.errors).items():
        errors.append(f'{k}: {"".join(v)}')
    return (f"Form submitting failed: {res.status_code}: {errors}",)


@pytest.mark.skip_models("constance.Config")
def test_admin_changeform(app: "DjangoTestApp", model_admin: "ModelAdmin[Model]", record: Model) -> None:
    opts: Options[Model] = model_admin.model._meta
    url = reverse_model_admin(model_admin, "change", args=[record.pk])

    res = app.get(url)
    assert str(opts.app_config.verbose_name) in res.body.decode()
    if model_admin.has_change_permission(Mock(user=app._user)):
        res = res.forms[1].submit()
        assert res.status_code in [302, 200]


@pytest.mark.skip_models("constance.Config", "bitcaster.MediaFile")
def test_admin_add(app: "DjangoTestApp", model_admin: "ModelAdmin[Model]") -> None:
    url = reverse_model_admin(model_admin, "add")
    if model_admin.has_add_permission(Mock(user=app._user)):
        res = app.get(url)
        res = res.forms[1].submit()
        assert res.status_code in [200, 302], log_submit_error(res)
    else:
        pytest.skip("No 'add' permission")


@pytest.mark.skip_models("constance.Config", "webpush.Browser", "bitcaster.Organization")
def test_admin_delete(
    app: "DjangoTestApp", model_admin: "ModelAdmin[Model]", record: Model, monkeypatch: "MonkeyPatch"
) -> None:
    url = reverse(admin_urlname(model_admin.model._meta, mark_safe("delete")), args=[record.pk])
    if model_admin.has_delete_permission(Mock(user=app._user)):
        res = app.get(url)
        res.forms[1].submit()
        assert res.status_code in [200, 302]
    else:
        pytest.skip("No 'delete' permission")


@pytest.mark.skip_buttons("bitcaster.EventAdmin:subscribe")
def test_admin_buttons(
    app: "DjangoTestApp",
    model_admin: "ExtraButtonsMixin",
    button_handler: "ButtonHandler",
    record: "Model",
    monkeypatch: "MonkeyPatch",
) -> None:
    from admin_extra_buttons.handlers import LinkHandler

    if isinstance(button_handler, ChoiceHandler):
        pass
    elif isinstance(button_handler, LinkHandler):
        btn = button_handler.get_button({"original": record})
        button_handler.func(None, btn)
    else:
        if len(button_handler.sig.parameters) == 2:
            url = reverse(f"admin:{button_handler.url_name}")
        else:
            url = reverse(f"admin:{button_handler.url_name}", args=[record.pk])

        res = app.get(url)
        assert res.status_code in [200, 302]
