import sys

import click

from bitcaster.cli import need_setup


class FieldParamType(click.ParamType):

    @need_setup
    def convert(self, value, param, ctx):
        import django
        django.setup()
        from django.core.exceptions import ValidationError
        from bitcaster.models import User
        try:
            field = User._meta.get_field(self.name)
            return field.clean(value, None)
        except ValidationError as e:
            raise click.ClickException('; '.join(e.messages))


class EmailType(FieldParamType):
    name = 'email'


class PasswordType(FieldParamType):
    name = 'password'


Email = EmailType()
Password = PasswordType()


def _get_superuser():
    return click.confirm('Should this user be a superuser?', default=False)


@click.command()  # noqa: C901
@click.option('--email', type=Email)
@click.option('--password', type=Password)
@click.option('--superuser/--no-superuser', default=None, is_flag=True)
@click.option('--no-password', default=False, is_flag=True)
@click.option('--prompt/--no-input',
              default=True,
              help='Do not prompt for parameters',
              is_flag=True)
@click.pass_context
def createuser(ctx, email, password, superuser, no_password, prompt):
    "Create a new user."
    if prompt:
        if not email:
            email = click.prompt('Email')

        if not (password or no_password):
            password = click.prompt('Password')

        if superuser is None:
            superuser = click.confirm('Should this user be a superuser?', default=False)

    if superuser is None:
        superuser = False

    if not email:
        raise click.ClickException('Invalid or missing email address.')

    if not no_password and not password:
        raise click.ClickException('No password set and --no-password not passed.')

    import django
    django.setup()

    from bitcaster.models import User

    user = User.objects.filter(email=email).first()

    if user:
        if prompt:
            change = click.confirm(f'User {email} already exists. Proceed updating it?', default=False)
            if not change:
                ctx.exit()
            user.set_password(password)
            if superuser:
                user.is_superuser = superuser

            op = "updated"
        else:
            click.echo('Nothing to do. User exists', err=True, color='red')
            sys.exit(1)
    else:
        op = "created"
        user = User(
            email=email,
            is_superuser=superuser,
            is_staff=superuser,
            is_active=True,
        )
        if password:
            user.set_password(password)

    try:
        user.save()
    except Exception as e:
        raise click.ClickException(e)

    click.echo(f'User {email} {op}')
