from strategy_field.utils import fqn

from bitcaster.dispatchers import GMmailDispatcher
from bitcaster.models import Channel


def test_manager_get_or_create(application):
    assert Channel.objects.get_or_create(dispatcher=fqn(GMmailDispatcher), application=application)
    assert Channel.objects.get_or_create(dispatcher=fqn(GMmailDispatcher), project=application.project)
    assert Channel.objects.get_or_create(
        dispatcher=fqn(GMmailDispatcher), organization=application.project.organization
    )

    assert Channel.objects.get_or_create(dispatcher=fqn(GMmailDispatcher), defaults={"application": application})
    assert Channel.objects.get_or_create(dispatcher=fqn(GMmailDispatcher), defaults={"project": application.project})
    assert Channel.objects.get_or_create(
        dispatcher=fqn(GMmailDispatcher), defaults={"organization": application.project.organization}
    )


def test_manager_update_or_create(application):
    assert Channel.objects.update_or_create(dispatcher=fqn(GMmailDispatcher), application=application)
    assert Channel.objects.update_or_create(dispatcher=fqn(GMmailDispatcher), project=application.project)
    assert Channel.objects.update_or_create(
        dispatcher=fqn(GMmailDispatcher), organization=application.project.organization
    )

    assert Channel.objects.update_or_create(dispatcher=fqn(GMmailDispatcher), defaults={"application": application})
    assert Channel.objects.update_or_create(dispatcher=fqn(GMmailDispatcher), defaults={"project": application.project})
    assert Channel.objects.update_or_create(
        dispatcher=fqn(GMmailDispatcher), defaults={"organization": application.project.organization}
    )


def test_manager_active(channel):
    assert Channel.objects.active()


def test_str(channel):
    assert str(channel)


def test_properties(channel):
    assert str(channel.from_email)
    assert str(channel.subject_prefix)
