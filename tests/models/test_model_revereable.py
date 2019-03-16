import pytest
from django.urls import NoReverseMatch

from bitcaster.models import Application, Channel, Subscription
from bitcaster.models.mixins import ReverseWrapper
from bitcaster.utils.tests.factories import factories_registry

pytestmark = pytest.mark.django_db


def test_reversewrapper(application1):
    obj = ReverseWrapper(application1)
    assert obj.edit


def test_reversewrapper_error(application1):
    obj = ReverseWrapper(application1)
    with pytest.raises(NoReverseMatch):
        assert obj.blahblah


def test_reversewrapper_cached(application1):
    obj = ReverseWrapper(application1)
    assert obj.edit
    assert obj.edit


@pytest.mark.parametrize('model', [Channel, Application, Subscription])
def test_reversewrapper_model_edit(model):
    instance = factories_registry[model]()
    assert instance.urls.delete
