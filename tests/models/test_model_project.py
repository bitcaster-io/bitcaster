from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bitcaster.models import Organization, Project, User


def test_str(project: "Project"):
    assert str(project) == project.name


def test_set_owner(organization: "Organization", user: "User"):
    from bitcaster.models import Project

    p = Project.objects.create(organization=organization)
    assert p.owner == organization.owner

    p = Project.objects.create(organization=organization, owner=user)
    assert p.owner == user
