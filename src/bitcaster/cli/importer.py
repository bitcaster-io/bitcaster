import click

from bitcaster.importing.members import import_members_csv
from bitcaster.models import Group, Organization


@click.group()
def importer():
    """Import data into Bitcaster."""


@importer.command(name="users")
@click.argument("csv_file", type=click.File("rb"))
@click.option("--org", help="Organization slug (defaults to first local organization)")
@click.option("--group", help="Optional Group name to add users to")
def import_users(csv_file, org, group):
    """Import users from a CSV file into a specific Organization."""
    try:
        if org:
            organization = Organization.objects.get(slug=org)
        else:
            organization = Organization.objects.local().first()
            if not organization:
                click.secho("Error: No local organization found.", fg="red")
                return

        group_obj = None
        if group:
            group_obj = Group.objects.get(organization=organization, name=group)

        # Configuriamo l'organizzazione corrente per il processo di importazione
        from bitcaster.constants import bitcaster

        bitcaster.local_organization = organization

        click.echo(f"Importing users into organization '{organization.name}'...")

        created, processed = import_members_csv(csv_file, group=group_obj)

        click.secho(f"Success! Processed {processed} lines, created/updated {created} users.", fg="green")
    except Organization.DoesNotExist:
        click.secho(f"Error: Organization '{org}' not found.", fg="red")
    except Group.DoesNotExist:
        click.secho(f"Error: Group '{group}' not found in organization '{org}'.", fg="red")
    except Exception as e:
        click.secho(f"An error occurred: {e}", fg="red")
