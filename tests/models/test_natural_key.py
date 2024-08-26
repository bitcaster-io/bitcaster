from typing import TYPE_CHECKING, Any, Mapping, Type

import pytest
from django.db.models import Model
from testutils.factories.base import AutoRegisterModelFactory

if TYPE_CHECKING:
    from pytest import FixtureRequest, Metafunc

KWARGS: Mapping[str, Any] = {}


def pytest_generate_tests(metafunc: "Metafunc") -> None:
    import django

    django.setup()
    if "model" in metafunc.fixturenames:
        from django.apps import AppConfig, apps

        m = []
        ids = []
        cfg: AppConfig = apps.get_app_config("bitcaster")
        for model in cfg.get_models():
            m.append(model)
            ids.append(model.__name__)
        metafunc.parametrize("model", m, ids=ids)


@pytest.fixture()
def record(db: Any, request: "FixtureRequest") -> Model:
    from testutils.factories import get_factory_for_model

    model = request.getfixturevalue("model")
    instance: Model = model.objects.first()
    if not instance:
        full_name = f"{model._meta.app_label}.{model._meta.object_name}"
        factory: type[AutoRegisterModelFactory[Any]] = get_factory_for_model(model)
        try:
            instance = factory(**KWARGS.get(full_name, {}))
        except Exception as e:
            raise Exception(f"Error creating fixture for {factory} using {KWARGS}") from e
    return instance


def test_natural_key(model: "Type[Model]", record: Model) -> None:
    key = record.natural_key()  # type: ignore[attr-defined]
    assert all([isinstance(m, (int | str | None)) for m in key]), key
    assert model.objects.get_by_natural_key(*key) == record, key  # type: ignore[attr-defined]
