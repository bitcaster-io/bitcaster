import logging
from unittest import mock

import pytest

from bitcaster.models import Organization
from bitcaster.utils.reflect import fqn
from bitcaster.utils.slug import slugify_instance
from bitcaster.utils.tests.factories import OrganizationFactory

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.django_db


class DummyQS:
    def __init__(self, target):
        self.target = target

    def __getattr__(self, item):
        return self.target.objects.all()

    def __call__(self, *a, **kw):
        return self.target.objects.all


@pytest.mark.parametrize('slug', ['', 'abc', 'reserved'])
def test_slugify_instance(organization1, slug):
    slugify_instance(organization1, slug, reserved=('reserved',))
    assert organization1.slug


def test_slugify_instance_conflict():
    OrganizationFactory(name='org1', slug='org1')
    org = Organization()
    slugify_instance(org, 'org1', reserved=('reserved',), )
    assert org.slug


def test_slugify_instance_simple_collision(organization1):
    collision = OrganizationFactory(slug='slug')

    slugify_instance(organization1, collision.slug, reserved=('reserved',), )
    assert organization1.slug

    with mock.patch('%s.objects.all' % fqn(Organization), DummyQS(Organization)):
        slugify_instance(organization1, collision.slug, reserved=('reserved',), )
        assert organization1.slug


def test_slugify_instance_fail():
    collision = OrganizationFactory(slug='slug')
    org = Organization()
    with mock.patch('%s.objects.all' % fqn(Organization), DummyQS(Organization)):
        slugify_instance(org, collision.slug, reserved=('reserved',), )
    assert org.slug


def test_slugify_instance_kwargs():
    collision = OrganizationFactory(slug='slug')
    org = Organization()
    with mock.patch('%s.objects.all' % fqn(Organization), DummyQS(Organization)):
        slugify_instance(org, collision.slug, aaa=1, reserved=('reserved',), )
    assert org.slug
