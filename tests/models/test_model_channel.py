from typing import TYPE_CHECKING, Any

import pytest
from strategy_field.utils import fqn, get_attr
from testutils.factories import ChannelFactory

from bitcaster.dispatchers import GMailDispatcher
from bitcaster.models import Channel, Project

if TYPE_CHECKING:
    from pytest import FixtureRequest


@pytest.fixture
def channel(request: "FixtureRequest", db: "Any") -> Channel:
    from testutils.factories.channel import ChannelFactory

    if hasattr(request, "param"):
        if request.param == "organization":
            return ChannelFactory(name="organization", project=None, organization__from_email="from@org")
        elif request.param == "project":
            return ChannelFactory(name="project", project__from_email="from@org")
    return ChannelFactory()


def test_manager_get_or_create(project: "Project") -> None:
    assert Channel.objects.get_or_create(dispatcher=fqn(GMailDispatcher), project=project)
    assert Channel.objects.get_or_create(dispatcher=fqn(GMailDispatcher), organization=project.organization)

    assert Channel.objects.get_or_create(dispatcher=fqn(GMailDispatcher), defaults={"project": project})
    assert Channel.objects.get_or_create(
        dispatcher=fqn(GMailDispatcher), defaults={"organization": project.organization}
    )


def test_manager_update_or_create(project: "Project") -> None:
    assert Channel.objects.update_or_create(dispatcher=fqn(GMailDispatcher), project=project)
    assert Channel.objects.update_or_create(dispatcher=fqn(GMailDispatcher), organization=project.organization)

    assert Channel.objects.update_or_create(dispatcher=fqn(GMailDispatcher), defaults={"project": project})
    assert Channel.objects.update_or_create(
        dispatcher=fqn(GMailDispatcher), defaults={"organization": project.organization}
    )


def test_manager_active(channel: "Channel") -> None:
    assert Channel.objects.active()


def test_str(channel: "Channel") -> None:
    assert str(channel)


@pytest.mark.parametrize("channel", ["organization", "project"], indirect=True)
def test_channel_owner(channel: "Channel") -> None:
    assert getattr(channel, "owner")


@pytest.mark.parametrize("channel", ["organization", "project"], indirect=True)
@pytest.mark.parametrize("attr", ["from_email", "subject_prefix"])
def test_channel_property(channel: "Channel", attr: str) -> None:
    assert getattr(channel, attr) == get_attr(channel, f"{channel.name}.{attr}")


@pytest.mark.parametrize("channel", ["organization", "project"], indirect=True)
@pytest.mark.parametrize("attr", ["from_email", "subject_prefix"])
def test_clean(channel: "Channel", attr: str) -> None:
    channel.clean()


@pytest.mark.parametrize("args", [{}, {"project": None}])
def test_natural_key(args: dict[str, Any]) -> None:
    ch = ChannelFactory(name="ch1", **args)
    assert Channel.objects.get_by_natural_key(*ch.natural_key()) == ch, ch.natural_key()
