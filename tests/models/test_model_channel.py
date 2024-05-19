import pytest
from strategy_field.utils import fqn, get_attr
from testutils.factories import ChannelFactory

from bitcaster.dispatchers import GMailDispatcher
from bitcaster.models import Channel


@pytest.fixture
def channel(request, db):
    from testutils.factories.channel import ChannelFactory

    if hasattr(request, "param"):
        if request.param == "organization":
            return ChannelFactory(name="organization", project=None, organization__from_email="from@org")
        elif request.param == "project":
            return ChannelFactory(name="project", project__from_email="from@org")
    return ChannelFactory()


def test_manager_get_or_create(project):
    assert Channel.objects.get_or_create(dispatcher=fqn(GMailDispatcher), project=project)
    assert Channel.objects.get_or_create(dispatcher=fqn(GMailDispatcher), organization=project.organization)

    assert Channel.objects.get_or_create(dispatcher=fqn(GMailDispatcher), defaults={"project": project})
    assert Channel.objects.get_or_create(
        dispatcher=fqn(GMailDispatcher), defaults={"organization": project.organization}
    )


def test_manager_update_or_create(project):
    assert Channel.objects.update_or_create(dispatcher=fqn(GMailDispatcher), project=project)
    assert Channel.objects.update_or_create(dispatcher=fqn(GMailDispatcher), organization=project.organization)

    assert Channel.objects.update_or_create(dispatcher=fqn(GMailDispatcher), defaults={"project": project})
    assert Channel.objects.update_or_create(
        dispatcher=fqn(GMailDispatcher), defaults={"organization": project.organization}
    )


def test_manager_active(channel):
    assert Channel.objects.active()


def test_str(channel):
    assert str(channel)


@pytest.mark.parametrize("channel", ["organization", "project"], indirect=True)
def test_channel_owner(channel: "Channel"):
    assert getattr(channel, "owner")


@pytest.mark.parametrize("channel", ["organization", "project"], indirect=True)
@pytest.mark.parametrize("attr", ["from_email", "subject_prefix"])
def test_channel_property(channel: "Channel", attr: str):
    assert getattr(channel, attr) == get_attr(channel, f"{channel.name}.{attr}")


@pytest.mark.parametrize("channel", ["organization", "project"], indirect=True)
@pytest.mark.parametrize("attr", ["from_email", "subject_prefix"])
def test_clean(channel: "Channel", attr: str):
    channel.clean()


@pytest.mark.parametrize("args", [{}, {"project": None}])
def test_natural_key(args):
    ch = ChannelFactory(name="ch1", **args)
    assert Channel.objects.get_by_natural_key(*ch.natural_key()) == ch, ch.natural_key()
