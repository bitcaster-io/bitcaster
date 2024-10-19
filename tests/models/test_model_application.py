from typing import TYPE_CHECKING

from bitcaster.models import Application

if TYPE_CHECKING:
    from bitcaster.models import Event, Project, User


def test_str(application: "Application") -> None:
    assert str(application) == application.name


def test_manager(application: "Application") -> None:
    assert Application.objects.local()


def test_set_owner(project: "Project", user: "User") -> None:
    from bitcaster.models import Application

    a = Application.objects.create(name="App1", project=project)
    assert a.owner == project.owner

    a = Application.objects.create(name="App2", project=project, owner=user)
    assert a.owner == user


def test_register_event(application: "Application") -> None:
    ev: "Event" = application.register_event("test_event")
    assert ev.name == "test_event"
    assert ev.application == application
