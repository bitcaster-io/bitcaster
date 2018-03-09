import click
from constance import config


@click.group()
@click.pass_context
def option(ctx, **kwargs):
    pass


@option.command(name="set")
@click.argument('name')
@click.argument('value')
def option_set(name, value, **kwargs):
    import constance.settings
    _type = constance.settings.CONFIG[name][2]
    if _type is bool:
        value = str(value).lower() in ["1", "true", "t"]
    else:
        value = _type(value)
    setattr(config, name, value)


@option.command(name='get')
@click.argument('name')
def option_get(name, **kwargs):
    click.echo(getattr(config, name))


@option.command(name="del")
@click.argument('name')
def option_delete(name, **kwargs):
    try:
        delattr(config, name)
        click.echo(getattr(config, name))
    except AttributeError:
        pass


@option.command(name="list")
def _list(**kwargs):
    import constance.settings
    for name, attrs in constance.settings.CONFIG.items():
        default, help_text, _type = attrs
        value = getattr(config, name)
        changed = '****' if (value != default) else ''
        click.echo(f"{name} {value} {changed}")
