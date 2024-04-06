from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bitcaster.models import ApiKey


def test_notify(api_key: "ApiKey"):
    assert api_key.application.project.organization.name == "Organization-000"
    assert api_key.application.project.name == "Project-000"
    assert api_key.application.name == "Application-000"
