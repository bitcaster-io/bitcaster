# decorator for Model.methods to enable async calls
# based on
# https://gist.github.com/fermayo/6f009162bf4a9576ddf6721a88b41b13
import importlib
from functools import wraps

from bitcaster.celery import app


@app.task
def call_async_task(obj_module_name, obj_class_name, obj_id, obj_method, obj_args=None, obj_kwargs=None):
    model_class = getattr(importlib.import_module(obj_module_name), obj_class_name)
    obj = model_class.objects.get(id=obj_id)
    method = getattr(obj, obj_method)
    obj_args = obj_args or []
    obj_kwargs = obj_kwargs or {}
    obj_kwargs.update({'async': False})
    return method(*obj_args, **obj_kwargs)


def call_async(args: list, **async_kwargs):
    obj, obj_method, obj_args, obj_kwargs = args

    return call_async_task.apply_async(
        args=[obj.__module__, obj.__class__.__name__, obj.id, obj_method, obj_args, obj_kwargs],
        **async_kwargs)


def async(**async_kwargs):
    def inner(f):
        @wraps(f)
        def func(self, *args, **kwargs):
            if kwargs.pop('async', True):
                args = [self, func.__name__, args, kwargs]
                return call_async(args, **async_kwargs)
            return f(self, *args, **kwargs)

        return func

    return inner
