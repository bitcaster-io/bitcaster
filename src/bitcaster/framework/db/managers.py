from django.db import models


class SmartManager(models.Manager):
    def get(self, *args, **kwargs):
        try:
            return super().get(*args, **kwargs)
        except self.model.DoesNotExist:
            raise self.model.DoesNotExist(
                '%s matching query does not exist. Using %s %s' %
                (self.model._meta.object_name, args, kwargs)
            )
