# -*- coding: utf-8 -*-
import pkg_resources
from django.conf import settings
from strategy_field.registry import Registry as Registry
from strategy_field.utils import fqn

from mercury.exceptions import PluginValidationError
from mercury.logging import getLogger

logger = getLogger(__name__)

dispatcher_registry = Registry('mercury.dispatchers.base.Dispatcher')

if settings.PLUGINS_AUTOLOAD:
    for ep in pkg_resources.iter_entry_points('mercury'):  # pragma: no-cover
        try:
            plugin = ep.load()
            if plugin in dispatcher_registry:
                logger.info('Plugin %s loaded' % fqn(plugin))
            else:
                logger.info('%s is not a plugin' % fqn(plugin))
        except (pkg_resources.DistributionNotFound, ImportError) as e:
            logger.exception(e)
        except pkg_resources.VersionConflict as e:
            raise PluginValidationError(
                "Plugin %r could not be loaded: %s!" % (ep.name, e))
        # else:
        #     if plugin not in dispatcher_registry:
        #         dispatcher_registry.append(plugin)
        #         logger.info('Dispatcher registered')
        #     else:
        #         logger.info('Dispatcher %s already registered' % fqn(plugin))
