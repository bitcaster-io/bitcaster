import getpass

import click
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management import CommandError

from bitcaster.cli import need_setup


def _get_pass(prompt='Password: '):
    p = getpass.getpass(prompt=prompt)
    if not p:
        raise CommandError('aborted')
    return p


@click.command()  # noqa: C901
@click.argument('username', required=False, default=None)
@click.option('-s', '--skip-validation', is_flag=True, default=False)
@click.pass_context
@need_setup
def changepassword(ctx, username, skip_validation):
    from bitcaster.models import User

    if not username:
        username = getpass.getuser()

    try:
        u = User.objects.get(email=username)
    except User.DoesNotExist:
        raise ctx.fail("user '%s' does not exist" % username)

    MAX_TRIES = 3
    count = 0
    p1, p2 = 1, 2  # To make them initially mismatch.
    password_validated = False
    while (p1 != p2 or not password_validated) and count < MAX_TRIES:
        p1 = _get_pass()
        p2 = _get_pass('Password (again): ')
        if p1 != p2:
            click.echo('Passwords do not match. Please try again.\n')
            count += 1
            # Don't validate passwords that don't match.
            continue
        if skip_validation:
            password_validated = True
        else:
            try:
                validate_password(p2, u)
            except ValidationError as err:
                click.echo('\n'.join(err.messages))
                count += 1
            else:
                password_validated = True

    if count == MAX_TRIES:
        raise ctx.fail("Aborting password change for user '%s' after %s attempts" % (u, count))

    u.set_password(p1)
    u.save()
    click.echo('Password changed')
