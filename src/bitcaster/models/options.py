from celery.signals import task_postrun
from django.core.cache import cache
from django.core.signals import request_finished
from django.db import models

from bitcaster.db.fields import EncryptedPickledObjectField

from .base import sane_repr
from .organization import Organization


class OptionManager(models.Manager):
    model_field = ""

    def __init__(self, *args, **kwargs):
        super(OptionManager, self).__init__(*args, **kwargs)
        self.__cache = {}

    def __getstate__(self):
        d = self.__dict__.copy()
        # we cant serialize weakrefs
        d.pop('_OrganizationOptionManager__cache', None)
        return d

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.__cache = {}

    def _make_key(self, instance_id):
        assert instance_id
        return '%s:%s' % (self.model._meta.db_table, instance_id)

    def get_value_bulk(self, instances, key):
        instance_map = dict((i.id, i) for i in instances)
        queryset = self.filter(
            organization__in=instances,
            key=key,
        )
        result = dict((i, None) for i in instances)
        for obj in queryset:
            result[instance_map[obj.organization_id]] = obj.value
        return result

    def get_value(self, owner, key, default=None):
        result = self.get_all_values(owner)
        return result.get(key, default)

    def unset_value(self, owner, key):
        try:
            inst = self.get(**{self.model_field: owner, "key": key})
        except self.model.DoesNotExist:
            return
        inst.delete()
        self.reload_cache(owner.id)

    def set_value(self, owner, key, value):
        self.create_or_update(**{
            self.model_field: owner,
            "key": key,
            "values": {
                'value': value,
            },
        })
        self.reload_cache(owner.id)

    def get_all_values(self, owner):
        if isinstance(owner, models.Model):
            owner_id = owner.id
        else:
            owner_id = owner

        if owner_id not in self.__cache:
            cache_key = self._make_key(owner_id)
            result = cache.get(cache_key)
            if result is None:
                result = self.reload_cache(owner_id)
            else:
                self.__cache[owner_id] = result
        return self.__cache.get(owner_id, {})

    def clear_local_cache(self, **kwargs):
        self.__cache = {}

    def reload_cache(self, owner_id):
        cache_key = self._make_key(owner_id)
        result = dict(
            (i.key, i.value)
            for i in self.filter(organization=owner_id)
        )
        cache.set(cache_key, result)
        self.__cache[owner_id] = result
        return result

    def post_save(self, instance, **kwargs):
        self.reload_cache(instance.organization_id)

    def post_delete(self, instance, **kwargs):
        self.reload_cache(instance.organization_id)

    def contribute_to_class(self, model, name):
        super(OptionManager, self).contribute_to_class(model, name)
        task_postrun.connect(self.clear_local_cache)
        request_finished.connect(self.clear_local_cache)


class Option(models.Model):
    """
    Organization options apply only to an instance of a organization.

    Options which are specific to a plugin should namespace
    their key. e.g. key='myplugin:optname'

    key: onboarding:complete
    value: { updated: datetime }
    """
    __core__ = True

    key = models.CharField(max_length=64)
    value = EncryptedPickledObjectField()

    objects = OptionManager()

    class Meta:
        abstract = True


class OrganizationOption(Option):
    """
    Organization options apply only to an instance of a organization.

    Options which are specific to a plugin should namespace
    their key. e.g. key='myplugin:optname'

    key: onboarding:complete
    value: { updated: datetime }
    """
    organization = models.ForeignKey(Organization,
                                     on_delete=models.CASCADE,
                                     related_name='options')

    class Meta:
        unique_together = (('organization', 'key',),)

    __repr__ = sane_repr('organization_id', 'key', 'value')
