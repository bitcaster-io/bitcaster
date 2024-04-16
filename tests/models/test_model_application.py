from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bitcaster.models import Application, Event, Project, User


def test_str(application: "Application"):
    assert str(application) == application.name


def test_set_owner(project: "Project", user: "User"):
    from bitcaster.models import Application

    a = Application.objects.create(project=project)
    assert a.owner == project.owner

    a = Application.objects.create(project=project, owner=user)
    assert a.owner == user


def test_register_event(application: "Application"):
    ev: "Event" = application.register_event("test_event")
    assert ev.name == "test_event"
    assert ev.application == application