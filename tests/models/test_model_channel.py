from typing import Any

import pytest

from strategy_field.utils import fqn, get_attr

from bitcaster.dispatchers import GMailDispatcher
from bitcaster.models import Channel, Project


@pytest.fixture
def channel(request: pytest.FixtureRequest, db: "Any") -> Channel:
    from testutils.factories.channel import ChannelFactory

    params = {
        "organization__email": "from@org",
    }
    match getattr(request, "param", None):
        case "organization":
            params.update({"project": None, "name": "organization"})
        case "project":
            params.update({"name": "project", "project__email": "from@prj"})
    return ChannelFactory.create(**params)


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
    assert channel.owner


@pytest.mark.parametrize("channel", ["organization", "project"], indirect=True)
@pytest.mark.parametrize("attr", ["from_email", "subject_prefix"])
def test_channel_property(channel: "Channel", attr: str) -> None:
    assert getattr(channel, attr) == get_attr(channel, f"{channel.name}.{attr}")


@pytest.mark.parametrize("channel", ["organization", "project"], indirect=True)
@pytest.mark.parametrize("attr", ["from_email", "subject_prefix"])
def test_clean(channel: "Channel", attr: str) -> None:
    channel.clean()


def test_channel_can_be_locked(channel: "Channel") -> None:
    assert channel.can_be_locked()


@pytest.mark.parametrize("args", [{}, {"project": None}])
def test_natural_key(args: dict[str, Any]) -> None:
    from testutils.factories import ChannelFactory

    ch = ChannelFactory.create(name="ch1", **args)
    assert Channel.objects.get_by_natural_key(*ch.natural_key()) == ch, ch.natural_key()
