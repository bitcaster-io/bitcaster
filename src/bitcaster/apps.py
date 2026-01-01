from django.apps import AppConfig
from flags.conditions.registry import _conditions


class Config(AppConfig):
    verbose_name = "Bitcaster"
    name = "bitcaster"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        from . import checks  # noqa
        from . import handlers as global_handlers  # noqa
        from .cache import handlers as cache_handlers  # noqa
        from .admin import register  # noqa
        from .utils import flags  # noqa

        for cond in ["parameter", "path matches", "after date", "before date", "anonymous"]:
            if cond in _conditions:  # pragma: no branch
                del _conditions[cond]
