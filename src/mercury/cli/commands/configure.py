import re
from functools import lru_cache
from pathlib import Path

import click


class AddressParamType(click.ParamType):
    name = 'address'

    def __call__(self, value, param=None, ctx=None):
        return self.convert(value, param, ctx)

    def convert(self, value, param, ctx):
        if callable(param.default):
            defaults = param.default().split(":")
        elif isinstance(param.default, str):
            defaults = param.default.split(":")
        else:
            defaults = ('', '')
        if not value:
            host, port = defaults
        elif ':' in value:
            host, port = value.split(':', 1)
            port = int(port)
        else:
            host = value
            port = defaults[1]
        return ":".join([host, str(port)])


Address = AddressParamType()


def read_current_env(param):
    ctx = click.get_current_context()
    env = ctx.obj['env']
    # env = ctx['env']
    return env(param)


@lru_cache(1)
def get_database_url_param():
    ctx = click.get_current_context()
    env = ctx.obj['env']

    rex = re.compile(r"psql://(?P<user>.*):(?P<password>.*)@(?P<host>.*):(?P<port>[0-9]+)/(?P<database>.*)")
    try:
        m = rex.match(env('DATABASE_URL'))
        return m.groupdict()
    except TypeError:
        return {'host': 'localhost',
                'port': 5432,
                'user': 'postgres',
                'password': '',
                'database': 'mercury'}


@click.command()
@click.option('--debug',
              default=False,
              is_flag=True)
# @click.option('--no-input', default=False, is_flag=True, help='debug mode')
# @click.option('--admin-email',
#               envvar='ADMIN_EMAIL',
#               default=lambda: read_current_env('ADMIN_EMAIL'),
#               help="Administrator email", prompt=True)
# @click.option('--admin-password',
#               envvar='MERCURY_ADMIN_PASSWORD',
#               help="Administrator password",
#               metavar='PASSWORD', prompt=True, hide_input=True,
#               confirmation_prompt=True)
# @click.option('--email-port',
#               default=lambda: read_current_env('EMAIL_PORT'),
#               type=click.INT)
# @click.option('--email-use-tls',
#               default=lambda: read_current_env('EMAIL_USE_TLS'),
#               is_flag=True)
# @click.option('--email-host',
#               default=lambda: read_current_env('EMAIL_HOST'),
#               prompt=True)
# @click.option('--email-host-user',
#               default=lambda: read_current_env('EMAIL_HOST_USER'),
#               metavar='USERNAME')
# @click.option('--email-host-password',
#               default=lambda: read_current_env('EMAIL_HOST_PASSWORD'),
#               metavar='PASSWORD',
#               hide_input=True, confirmation_prompt=True)
@click.option('--redis-host',
              envvar='MERCURY_REDIS_HOST',
              default=lambda: read_current_env('REDIS_HOST'),
              prompt=True)
@click.option('--database-address',
              default=lambda: "{0[host]}:{0[port]}".format(get_database_url_param()),
              prompt=True,
              type=Address
              )
@click.option('--database-user',
              default=lambda: get_database_url_param()["user"],
              prompt=True)
@click.option('--database-password',
              default=lambda: get_database_url_param()["password"],
              prompt=True)
@click.option('--database-name',
              default=lambda: get_database_url_param()["database"],
              prompt=True)
@click.pass_context
def configure(ctx, debug, database_user, database_password,
              database_address, database_name, **kwargs):
    cfg_file = Path(ctx.obj['config'])

    click.echo(f"Configuration file: {cfg_file}")
    env = ctx.obj['env']
    # if not cfg_file.exists():
    #     cfg_file.parent.mkdir(mode=0o770,  parents=True)
    #     cfg_file.touch(mode=0o660)
    # env.load_config(cfg_file)
    env.ENVIRON['DEBUG'] = str(debug)
    env.ENVIRON['DATABASE_URL'] = f"psql://{database_user}:{database_password}@{database_address}/{database_name}"
    env.write_env(cfg_file)
