from django.apps import AppConfig

# def _get_permission_codename(action, opts):
#     return '%s_%s' % (action, opts.object_name.lower())
#
#
# def create_extra_permission(sender, **kwargs):
#     from django.contrib.auth.models import Permission
#     from django.contrib.contenttypes.models import ContentType
#
#     models = sender.get_models()
#
#     for model in models:
#         for action in ('view',):
#             opts = model._meta
#             codename = _get_permission_codename(action, opts)
#             label = u'Can %s %s' % (action, opts.verbose_name_raw)
#             ct = ContentType.objects.get_for_model(model)
#             Permission.objects.get_or_create(codename=codename,
#                                              content_type=ct,
#                                              defaults={'name': label})


class Config(AppConfig):
    name = 'mercury'

    def ready(self):
        from . import celery  # noqa
        from django.conf import settings  # noqa
        from .dispatchers.registry import dispatcher_registry  # noqa
        from . import tasks  # noqa
        from . import checks  # noqa

# post_migrate.connect(create_extra_permission,
#                      dispatch_uid='create_extra_permission')
