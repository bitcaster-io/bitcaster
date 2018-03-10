import json
from pathlib import Path

import click

from bitcaster.cli import need_setup
from bitcaster.cli.commands.option import option_set
from bitcaster.utils.json import Decoder, Encoder


@click.command()
@click.option('--file',
              'filename',
              default=str(Path('~/.bitcaster/backups/1.json').expanduser()),
              type=click.Path())
@click.pass_context
@need_setup
def backup(ctx, filename, **kwargs):
    from bitcaster.models import Channel
    from constance import config, settings as sett

    try:
        data = {}
        data['channels'] = list(Channel.objects.filter(system=True).values())
        data['options'] = [(key, getattr(config, key)) for key, value in sett.CONFIG.items()]

        output = Path(filename)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(data, cls=Encoder))
    except Exception as e:
        click.echo(str(e))
        ctx.abort()


@click.command()
@click.option('--file',
              'filename',
              default=str(Path('~/.bitcaster/backups/1.json').expanduser()),
              type=click.Path())
@click.pass_context
@need_setup
def restore(ctx, filename, **kwargs):
    from bitcaster.models import Channel

    try:
        input = Path(filename)
        data = json.loads(input.read_text(), cls=Decoder)
        for key, value in data['options']:
            ctx.invoke(option_set,
                       name=key,
                       value=value)
        for channel in data['channels']:
            del channel['id']
            del channel['last_modify_date']
            Channel.objects.get_or_create(**channel)
    except Exception as e:
        click.echo(str(e))
        ctx.abort()
