import io
from unittest.mock import patch

from bitcaster.cli.__main__ import cli


def test_cli_import_users_success(runner, organization):
    csv_content = b"email,first_name,last_name\nuser1@example.com,User,One\nuser2@example.com,User,Two"
    csv_file = io.BytesIO(csv_content)

    # We need to mock the file opening because click.File handles it
    with patch("click.File.convert", return_value=csv_file):
        result = runner.invoke(cli, ["import", "users", "dummy.csv", "--org", organization.slug])

    assert result.exit_code == 0
    assert "Importing users into organization" in result.output
    assert "Success! Processed 2 lines" in result.output
    assert organization.users.count() == 2


def test_cli_import_users_default_org(runner, local_organization):
    csv_content = b"email,first_name,last_name\nuser1@example.com,User,One"
    csv_file = io.BytesIO(csv_content)

    with patch("click.File.convert", return_value=csv_file):
        result = runner.invoke(cli, ["import", "users", "dummy.csv"])

    assert result.exit_code == 0
    assert f"Importing users into organization '{local_organization.name}'" in result.output
    assert "Success!" in result.output


def test_cli_import_users_no_org_found(runner, db):
    from bitcaster.models import Organization

    Organization.objects.all().delete()

    csv_content = b"email\nuser@example.com"
    csv_file = io.BytesIO(csv_content)

    with patch("click.File.convert", return_value=csv_file):
        result = runner.invoke(cli, ["import", "users", "dummy.csv"])

    assert "Error: No local organization found." in result.output


def test_cli_import_users_org_not_found(runner, db):
    csv_content = b"email\nuser@example.com"
    csv_file = io.BytesIO(csv_content)

    with patch("click.File.convert", return_value=csv_file):
        result = runner.invoke(cli, ["import", "users", "dummy.csv", "--org", "non-existent"])

    assert "Error: Organization 'non-existent' not found." in result.output


def test_cli_import_users_with_group(runner, organization, group):
    csv_content = b"email\nuser1@example.com"
    csv_file = io.BytesIO(csv_content)

    with patch("click.File.convert", return_value=csv_file):
        result = runner.invoke(cli, ["import", "users", "dummy.csv", "--org", organization.slug, "--group", group.name])

    assert result.exit_code == 0
    assert "Success!" in result.output
    assert organization.users.filter(username="user1@example.com").exists()


def test_cli_import_users_group_not_found(runner, organization):
    csv_content = b"email\nuser1@example.com"
    csv_file = io.BytesIO(csv_content)

    with patch("click.File.convert", return_value=csv_file):
        result = runner.invoke(
            cli, ["import", "users", "dummy.csv", "--org", organization.slug, "--group", "NonExistentGroup"]
        )

    assert f"Error: Group 'NonExistentGroup' not found in organization '{organization.slug}'." in result.output


def test_cli_import_users_exception(runner, organization):
    csv_content = b"email\nuser1@example.com"
    csv_file = io.BytesIO(csv_content)

    with patch("click.File.convert", return_value=csv_file):
        with patch("bitcaster.cli.importer.import_members_csv", side_effect=Exception("Unexpected error")):
            result = runner.invoke(cli, ["import", "users", "dummy.csv", "--org", organization.slug])

    assert "An error occurred: Unexpected error" in result.output
