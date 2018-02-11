# -*- coding: utf-8 -*-
from contextlib import ContextDecorator
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, Permission
from random import choice

import factory
from faker import Faker
from rest_framework.test import APIClient

import mercury
from mercury import models
from mercury.dispatchers import Email
from mercury.models.token import generate_token
from mercury.utils import fqn

whitespace = ' \t\n\r\v\f'
lowercase = 'abcdefghijklmnopqrstuvwxyz'
uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
letters = lowercase + uppercase
ascii_lowercase = lowercase
ascii_uppercase = uppercase
ascii_letters = ascii_lowercase + ascii_uppercase

faker = Faker()


def text(length, choices=ascii_letters):
    """ returns a random (fixed length) string

    :param length: string length
    :param choices: string containing all the chars can be used to build the string

    .. seealso::
       :py:func:`rtext`
    """
    return ''.join(choice(choices) for x in range(length))


def get_group(name=None, permissions=None):
    group = GroupFactory(name=(name or text(5)))
    permission_names = permissions or []
    for permission_name in permission_names:
        try:
            app_label, codename = permission_name.split('.')
        except ValueError:
            raise ValueError("Invalid permission name `{0}`".format(permission_name))
        try:
            permission = Permission.objects.get(content_type__app_label=app_label, codename=codename)
        except Permission.DoesNotExist:
            raise Permission.DoesNotExist('Permission `{0}` does not exists', permission_name)

        group.permissions.add(permission)
    return group


class user_grant_permissions(ContextDecorator):  # noqa
    caches = ['_group_perm_cache', '_user_perm_cache', '_dsspermissionchecker',
              '_officepermissionchecker', '_perm_cache', '_dss_acl_cache']

    def __init__(self, user, permissions=None):
        self.user = user
        self.permissions = permissions
        self.group = None

    def __enter__(self):
        for cache in self.caches:
            if hasattr(self.user, cache):
                delattr(self.user, cache)
        self.group = get_group(permissions=self.permissions or [])
        self.user.groups.add(self.group)

    def __exit__(self, e_typ, e_val, trcbak):
        if self.group:
            self.user.groups.remove(self.group)
            self.group.delete()

        if e_typ:
            raise e_typ(e_val).with_traceback(trcbak)

    def start(self):
        """Activate a patch, returning any created mock."""
        result = self.__enter__()
        return result

    def stop(self):
        """Stop an active patch."""
        return self.__exit__(None, None, None)


def client_factory(user, token=None, force=False):
    client = APIClient()
    if force:
        client.force_authenticate(user=user)
    else:
        assert client.login(username=user.username, password='123')
        client.handler._force_user = user
    return client


def api_client_factory(app):
    token = models.ApiAuthToken.objects.get(application=app)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.token)
    return client


class GroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = Group


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = mercury.models.user.User
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: "user%03d" % n)

    last_name = factory.Faker('last_name')
    first_name = factory.Faker('first_name')

    email = factory.Sequence(lambda n: "m%03d@mailinator.com" % n)
    password = '123'

    # is_active = True

    @classmethod
    def _get_or_create(cls, model_class, *args, **kwargs):
        permissions = kwargs.pop('permissions', [])
        raw_password = kwargs.pop('password', cls.password)
        kwargs['password'] = make_password(raw_password)
        user = super()._get_or_create(model_class, *args, **kwargs)
        # if password:
        #     user.set_password(password)
        if permissions:
            user_grant_permissions(user, permissions).start()
        return user


class AdminFactory(UserFactory):
    class Meta:
        model = models.User
        django_get_or_create = ('username',)

    is_superuser = True
    is_staff = True

    @factory.post_generation
    def tokens(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return
        ApiTokenFactory(user=self)


class ApplicationFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Application
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: "Application %03d" % n)
    owner = factory.SubFactory(UserFactory)

    @factory.post_generation
    def maintainers(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return
        ApiTokenFactory(application=self, user=self.owner)
        if extracted:
            # A list of groups were passed in, use them
            for user in extracted:
                self.maintainers.add(user)


class ApiTokenFactory(factory.DjangoModelFactory):
    application = factory.SubFactory(ApplicationFactory)
    user = factory.SubFactory(UserFactory)
    token = factory.LazyAttribute(lambda s: generate_token())
    refresh_token = factory.LazyAttribute(lambda s: generate_token())

    class Meta:
        model = models.ApiAuthToken
        django_get_or_create = ('token',)


class ChannelFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Channel
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: "Channel %03d" % n)
    application = factory.SubFactory(ApplicationFactory)
    handler = factory.LazyAttribute(lambda a: fqn(Email))
    enabled = True

    @classmethod
    def _get_or_create(cls, model_class, *args, **kwargs):
        if 'config' not in kwargs:
            kwargs['config'] = {'server': 'server',
                                'port': 9000,
                                'sender': 'sender@sender.org'}
        channel = super()._get_or_create(model_class, *args, **kwargs)
        return channel


class EventFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Event
        django_get_or_create = ('application', 'name')

    name = factory.Sequence(lambda n: "Event %03d" % n)
    application = factory.SubFactory(ApplicationFactory)


class MessageFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Message
        django_get_or_create = ('event', 'name',)

    name = factory.Sequence(lambda n: "Message %03d" % n)
    event = factory.SubFactory(EventFactory)
    language = factory.Iterator(['it', 'en', 'es', 'fr'])
    subject = factory.Sequence(lambda n: "Subject %03d" % n)
    body = factory.LazyAttribute(lambda n: faker.text(max_nb_chars=200), )

    @classmethod
    def _get_or_create(cls, model_class, *args, **kwargs):
        # channels = kwargs.pop('channels', None)
        message = super()._get_or_create(model_class, *args, **kwargs)
        message.clean()
        # if not channels:
        #     channels = [ChannelFactory(application=message.event.application)]
        #
        # for e in channels:
        #     message.channels.add(e)
        return message

    @factory.post_generation
    def channels(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return
        if not extracted:
            extracted = [ChannelFactory(application=self.event.application)]

        for e in extracted:
            self.channels.add(e)


class SubscriptionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Subscription
        django_get_or_create = ('subscriber', 'event', 'channel')

    subscriber = factory.SubFactory(UserFactory)
    channel = factory.SubFactory(ChannelFactory)
    event = factory.SubFactory(EventFactory)
    config = {}
