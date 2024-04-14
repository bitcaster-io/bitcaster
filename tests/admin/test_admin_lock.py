import pytest
from django.contrib.admin.sites import site
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.db.models.options import Options
from django.urls import reverse
from django_regex.utils import RegexList as _RegexList

pytestmark = [pytest.mark.admin, pytest.mark.smoke, pytest.mark.django_db]


class RegexList(_RegexList):
    def extend(self, __iterable) -> None:
        for e in __iterable:
            self.append(e)


GLOBAL_EXCLUDED_MODELS = RegexList(
    [
        r"django_celery_beat\.ClockedSchedule",
        r"contenttypes\.ContentType",
        "authtoken",
        "social_django",
        "depot",
    ]
)

GLOBAL_EXCLUDED_BUTTONS = RegexList(
    [
        "core.UserAdmin:link_user_data",
    ]
)

KWARGS = {}


def log_submit_error(res):
    try:
        return f"Submit failed with: {repr(res.context['form'].errors)}"
    except KeyError:
        return "Submit failed"


def pytest_generate_tests(metafunc):
    import django
    from bitcaster.admin.mixins import LockMixin

    markers = metafunc.definition.own_markers
    excluded_models = RegexList(GLOBAL_EXCLUDED_MODELS)
    if "skip_models" in [m.name for m in markers]:
        skip_rule = list(filter(lambda m: m.name == "skip_models", markers))[0]
        excluded_models.extend(skip_rule.args)
    django.setup()
    if "modeladmin" in metafunc.fixturenames:
        m = []
        ids = []
        for model, admin in site._registry.items():
            if isinstance(admin, LockMixin):
                name = model._meta.object_name
                full_name = f"{model._meta.app_label}.{name}"
                if not (full_name in excluded_models):
                    m.append(admin)
                    ids.append(f"{admin.__class__.__name__}:{full_name}")
        metafunc.parametrize("modeladmin", m, ids=ids)


@pytest.fixture()
def record(db, request):
    from testutils.factories import get_factory_for_model

    # TIPS: database access is forbidden in pytest_generate_tests
    modeladmin = request.getfixturevalue("modeladmin")
    instance = modeladmin.model.objects.first()
    if not instance:
        full_name = f"{modeladmin.model._meta.app_label}.{modeladmin.model._meta.object_name}"
        factory = get_factory_for_model(modeladmin.model)
        try:
            instance = factory(**KWARGS.get(full_name, {}))
        except Exception as e:
            raise Exception(f"Error creating fixture for {factory} using {KWARGS}") from e
    return instance


@pytest.fixture()
def app(django_app_factory, mocked_responses):
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def show_error(res):
    errors = []
    for k, v in dict(res.context["adminform"].form.errors).items():
        errors.append(f'{k}: {"".join(v)}')
    return (f"Form submitting failed: {res.status_code}: {errors}",)


def test_admin_lock(app, modeladmin, record):
    opts: Options = modeladmin.model._meta
    url = reverse(admin_urlname(opts, "change"), args=[record.pk])

    res = app.get(url)
    assert str(opts.app_config.verbose_name) in res.body.decode()
    res = res.click(".Lock$")
    assert res.status_code == 200
    res = res.forms["lock-form"].submit()
    assert res.status_code == 302
    record.refresh_from_db()
    assert record.locked


def test_admin_unlock(app, modeladmin, record):
    opts: Options = modeladmin.model._meta
    url = reverse(admin_urlname(opts, "change"), args=[record.pk])
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
# def test_admin_lock(app, modeladmin, record):
#     opts: Options = modeladmin.model._meta
#     url = reverse(admin_urlname(opts, "change"), args=[record.pk])
#
#     res = app.get(url)
#     assert str(opts.app_config.verbose_name) in res.body.decode()
#     res.click("lock")
#     assert res.status_code == 200
#     res.click("lock")
#     assert res.status_code == 302
#     assert record.locked
