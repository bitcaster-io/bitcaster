import pytest
from strategy_field.utils import fqn, get_attr

from bitcaster.dispatchers import GMailDispatcher
from bitcaster.models import Channel


@pytest.fixture
def channel(request, db):
    from testutils.factories.channel import ChannelFactory

    if hasattr(request, "param"):
        if request.param == "organization":
            return ChannelFactory(
                name="organization", project=None, application=None, organization__from_email="from@org"
            )
        elif request.param == "project":
            return ChannelFactory(name="project", application=None, project__from_email="from@org")
        elif request.param == "application":
            return ChannelFactory(name="application", application__from_email="from@app")
    return ChannelFactory()


def test_manager_get_or_create(application):
    assert Channel.objects.get_or_create(dispatcher=fqn(GMailDispatcher), application=application)
    assert Channel.objects.get_or_create(dispatcher=fqn(GMailDispatcher), project=application.project)
    assert Channel.objects.get_or_create(dispatcher=fqn(GMailDispatcher), organization=application.project.organization)

    assert Channel.objects.get_or_create(dispatcher=fqn(GMailDispatcher), defaults={"application": application})
    assert Channel.objects.get_or_create(dispatcher=fqn(GMailDispatcher), defaults={"project": application.project})
    assert Channel.objects.get_or_create(
        dispatcher=fqn(GMailDispatcher), defaults={"organization": application.project.organization}
    )


def test_manager_update_or_create(application):
    assert Channel.objects.update_or_create(dispatcher=fqn(GMailDispatcher), application=application)
    assert Channel.objects.update_or_create(dispatcher=fqn(GMailDispatcher), project=application.project)
    assert Channel.objects.update_or_create(
        dispatcher=fqn(GMailDispatcher), organization=application.project.organization
    )

    assert Channel.objects.update_or_create(dispatcher=fqn(GMailDispatcher), defaults={"application": application})
    assert Channel.objects.update_or_create(dispatcher=fqn(GMailDispatcher), defaults={"project": application.project})
    assert Channel.objects.update_or_create(
        dispatcher=fqn(GMailDispatcher), defaults={"organization": application.project.organization}
    )


def test_manager_active(channel):
    assert Channel.objects.active()


def test_str(channel):
    assert str(channel)


@pytest.mark.parametrize("channel", ["organization", "project", "application"], indirect=True)
@pytest.mark.parametrize("attr", ["from_email", "subject_prefix"])
def test_channel_property(channel: "Channel", attr: str):
    assert getattr(channel, attr) == get_attr(channel, f"{channel.name}.{attr}")


@pytest.mark.parametrize("channel", ["organization", "project", "application"], indirect=True)
@pytest.mark.parametrize("attr", ["from_email", "subject_prefix"])
def test_clean(channel: "Channel", attr: str):
    channel.clean()
