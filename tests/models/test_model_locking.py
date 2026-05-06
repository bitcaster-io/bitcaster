import pytest

from django.apps import apps


@pytest.mark.django_db
@pytest.mark.parametrize("model_name", ["Application", "Event"])
def test_locking(model_name):
    from testutils.factories import get_factory_for_model

    model = apps.get_model(f"bitcaster.{model_name.lower()}")
    factory = get_factory_for_model(model)
    target = factory()
    target.lock()
    assert target.locked
    target.lock()

    target.unlock()
    assert not target.locked
    target.unlock()


@pytest.mark.django_db
@pytest.mark.parametrize("model_name", ["Application", "Event"])
def test_pause(model_name):
    from testutils.factories import get_factory_for_model

    model = apps.get_model(f"bitcaster.{model_name.lower()}")
    factory = get_factory_for_model(model)
    target = factory()
    target.pause()
    assert target.paused
    target.pause()

    target.resume()
    assert not target.paused
    target.resume()
