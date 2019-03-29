import click

from bitcaster.cli import need_setup


def parse_bool(value):
    return value.lower() not in ['', '0', 'false', 'f', 'n']


caster = {bool: parse_bool,
          int: parse_bool,
          }


@click.command()
@click.argument('key', required=False, default=None)
@click.argument('value', required=False, default=None)
@click.pass_context
@need_setup
def option(ctx, key, value):
    from constance import config, settings
    if not key:
        for entry, __ in settings.CONFIG.items():
            click.echo('%s=%s' % (entry, str(getattr(config, entry))))
    elif value:
        try:
            default, help, type = settings.CONFIG[key]
            cast = caster.get(type, type)
            setattr(config, key, cast(value))
            click.echo('%s=%s' % (key, str(getattr(config, key))))
        except AttributeError:
            ctx.fail('%s is not a valid option' % key)
    else:
        click.echo('%s=%s' % (key, str(getattr(config, key))))
