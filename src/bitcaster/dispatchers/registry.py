from logging import getLogger

from strategy_field.registry import Registry

logger = getLogger(__name__)


dispatcher_registry = Registry('bitcaster.dispatchers.base.Dispatcher',
                               label_attribute='label')

#
# def load_plugins():
#     for ep in pkg_resources.iter_entry_points('bitcaster'):  # pragma: no-cover
#         try:
#             plugin = ep.load()
#             if plugin in dispatcher_registry:
#                 logger.info('Plugin %s loaded' % fqn(plugin))
#             else:
#                 logger.info('%s is not a plugin' % fqn(plugin))
#         except (pkg_resources.DistributionNotFound, ImportError, ModuleNotFoundError) as e:
#             logger.error(e)
#         except pkg_resources.VersionConflict as e:
#             raise PluginValidationError(
#                 'Plugin %r could not be loaded: %s!' % (ep.name, e))
#         else:
#             if plugin not in dispatcher_registry:
#                 dispatcher_registry.append(plugin)
#                 logger.info('Dispatcher registered')
#             else:
#                 logger.info('Dispatcher %s already registered' % fqn(plugin))
#
#
# if env.bool('PLUGINS_AUTOLOAD'):
#     load_plugins()
