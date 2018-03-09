from strategy_field.utils import fqn, import_by_name  # noqa


def package_name(c):
    return fqn(c).split('.')[0]
