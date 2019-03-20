# -*- coding: utf-8 -*-
from contextlib import ContextDecorator
from random import choice

import factory
from django.contrib.auth.models import Group, Permission
from factory.base import FactoryMetaClass
from faker import Faker
from rest_framework.test import APIClient

import bitcaster
from bitcaster import models
from bitcaster.agents import EmailAgent
from bitcaster.dispatchers import Email
from bitcaster.framework.db.fields import Role
from bitcaster.models.token import generate_api_token
from bitcaster.utils import fqn

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
            raise ValueError('Invalid permission name `{0}`'.format(permission_name))
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
        assert client.login(email=user.email, password='123')
        client.handler._force_user = user
    return client


def api_client_factory(app):
    token = models.ApiAuthToken.objects.get(application=app)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.token)
    return client


factories_registry = {}


class AutoRegisterFactoryMetaClass(FactoryMetaClass):
    def __new__(mcs, class_name, bases, attrs):
        new_class = super().__new__(mcs, class_name, bases, attrs)
        factories_registry[new_class._meta.model] = new_class
        return new_class


class AutoRegisterModelFactory(factory.DjangoModelFactory, metaclass=AutoRegisterFactoryMetaClass):
    pass


class GroupFactory(AutoRegisterModelFactory):
    class Meta:
        model = Group


class UserFactory(AutoRegisterModelFactory):
    class Meta:
        model = bitcaster.models.user.User
        django_get_or_create = ('email',)

    name = factory.Faker('name')

    email = factory.Sequence(lambda n: 'm%03d@example.com' % n)
    password = '123'
    is_active = True

    @classmethod
    def _get_or_create(cls, model_class, *args, **kwargs):
        permissions = kwargs.pop('permissions', None)
        addresses = kwargs.pop('addresses', None)
        raw_password = kwargs.pop('password', cls.password)
        user = super()._get_or_create(model_class, *args, **kwargs)
        if raw_password:
            user.set_password(raw_password)
        if permissions:
            user_grant_permissions(user, permissions).start()
        if addresses:
            for handler, address in addresses.items():
                user.addresses.create(label=handler,
                                      address=address)

        return user


class MemberFactory(UserFactory):
    role = Role.SUBSCRIBER

    @classmethod
    def _get_or_create(cls, model_class, *args, **kwargs):
        organization = kwargs.pop('organization')
        role = kwargs.pop('role')
        user = super()._get_or_create(model_class, *args, **kwargs)
        organization.add_member(user, role=role)

        return user


class AdminFactory(UserFactory):
    class Meta:
        model = models.User
        django_get_or_create = ('email',)

    is_superuser = True
    is_staff = True

    @factory.post_generation
    def tokens(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return
        ApiTokenFactory(user=self)


class OrganizationFactory(AutoRegisterModelFactory):
    name = factory.Sequence(lambda n: 'Organization %03d' % n)
    owner = factory.SubFactory(UserFactory)

    class Meta:
        model = models.Organization
        django_get_or_create = ('name',)

    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        super()._after_postgeneration(instance, create, results)
        instance.add_member(instance.owner, role=Role.OWNER)


class ApplicationFactory(AutoRegisterModelFactory):
    class Meta:
        model = models.Application
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: 'Application %03d' % n)
    organization = factory.SubFactory(OrganizationFactory)


class TeamFactory(AutoRegisterModelFactory):
    class Meta:
        model = bitcaster.models.Team
        django_get_or_create = ('name',)

    application = factory.SubFactory(ApplicationFactory)
    manager = factory.SubFactory(UserFactory)
    name = factory.Faker('name')
    # members = []

    # @classmethod
    # def _get_or_create(cls, model_class, *args, **kwargs):
    #     cls.members = kwargs.pop('members')
    #     return super()._get_or_create(model_class, *args, **kwargs)
    #
    # @classmethod
    # def _after_postgeneration(cls, instance, create, results=None):
    #     super()._after_postgeneration(instance, create, results)
    #     for member in cls.members:
    #         # m, __ = OrganizationMember.objects.get_or_create(
    #         #     organization=instance.organization,
    #         #     user=member
    #         # )
    #         TeamMembership.objects.create(team=instance, member=member)


class ApplicationRoleFactory(AutoRegisterModelFactory):
    class Meta:
        model = bitcaster.models.ApplicationRole
        django_get_or_create = ('team',)

    team = factory.SubFactory(TeamFactory)
    role = Role.SUBSCRIBER


class InvitationFactory(AutoRegisterModelFactory):
    class Meta:
        model = bitcaster.models.Invitation

    organization = factory.SubFactory(OrganizationFactory)


#
# class ApplicationTeamFactory(AutoRegisterModelFactory):
#     class Meta:
#         model = bitcaster.models.Team
#         django_get_or_create = ('name',)
#
#     application = factory.SubFactory(ApplicationFactory)
#     team = factory.SubFactory(TeamFactory)
#     role = Role.SUBSCRIBER


class ApplicationTriggerKeyFactory(AutoRegisterModelFactory):
    application = factory.SubFactory(ApplicationFactory)
    token = factory.LazyAttribute(lambda s: generate_api_token())

    class Meta:
        model = models.ApplicationTriggerKey
        django_get_or_create = ('token',)

    @classmethod
    def _get_or_create(cls, model_class, *args, **kwargs):
        events = kwargs.pop('events', None)
        key = super()._get_or_create(model_class, *args, **kwargs)
        if events:
            for e in events:
                key.events.add(e)
        return key


class ApiTokenFactory(AutoRegisterModelFactory):
    application = factory.SubFactory(ApplicationFactory)
    user = factory.SubFactory(UserFactory)
    token = factory.LazyAttribute(lambda s: generate_api_token())

    class Meta:
        model = models.ApiAuthToken
        django_get_or_create = ('token',)


class MonitorFactory(AutoRegisterModelFactory):
    class Meta:
        model = models.Monitor
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: 'Monitor %03d' % n)
    application = factory.SubFactory(ApplicationFactory)
    handler = factory.LazyAttribute(lambda a: fqn(EmailAgent))
    enabled = True

    @classmethod
    def _get_or_create(cls, model_class, *args, **kwargs):
        if 'config' not in kwargs:
            kwargs['config'] = {'event': EventFactory(application=kwargs['application']).pk,
                                'username': 'user',
                                'password': '111',
                                'server': 'mail.example.com',
                                'port': '123',
                                'folder': 'linkedin.com',
                                'body_regex': '',
                                'subject_regex': 'gerardo',
                                'sender_regex': '',
                                'to_regex': ''
                                }
        channel = super()._get_or_create(model_class, *args, **kwargs)
        return channel


class ChannelFactory(AutoRegisterModelFactory):
    class Meta:
        model = models.Channel
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: 'Channel %03d' % n)
    organization = factory.SubFactory(OrganizationFactory)
    # application = factory.SubFactory(ApplicationFactory)
    handler = factory.LazyAttribute(lambda a: fqn(Email))
    enabled = True
    deprecated = False

    @classmethod
    def _get_or_create(cls, model_class, *args, **kwargs):
        if 'config' not in kwargs:
            kwargs['config'] = {'server': 'server',
                                'backend': 'django.core.mail.backends.locmem.EmailBackend',
                                'port': 9000,
                                'sender': 'sender@sender.org'}
        channel = super()._get_or_create(model_class, *args, **kwargs)

        return channel


class EventFactory(AutoRegisterModelFactory):
    class Meta:
        model = models.Event
        django_get_or_create = ('application', 'name')

    name = factory.Sequence(lambda n: 'Event %03d' % n)
    application = factory.SubFactory(ApplicationFactory)


class MessageFactory(AutoRegisterModelFactory):
    class Meta:
        model = models.Message
        django_get_or_create = ('event', 'name',)

    name = factory.Sequence(lambda n: 'Message %03d' % n)
    event = factory.SubFactory(EventFactory)
    channel = factory.SubFactory(ChannelFactory)
    enabled = True
    language = factory.Iterator(['it', 'en', 'es', 'fr'])
    subject = factory.Sequence(lambda n: 'Subject %03d' % n)
    body = factory.LazyAttribute(lambda n: faker.text(max_nb_chars=200), )

    @classmethod
    def _get_or_create(cls, model_class, *args, **kwargs):
        message = super()._get_or_create(model_class, *args, **kwargs)
        message.clean()
        return message


class SubscriptionFactory(AutoRegisterModelFactory):
    class Meta:
        model = models.Subscription
        django_get_or_create = ('subscriber', 'event', 'channel')

    subscriber = factory.SubFactory(UserFactory)
    trigger_by = factory.SubFactory(AdminFactory)
    channel = factory.SubFactory(ChannelFactory)
    event = factory.SubFactory(EventFactory)
    config = {}

    @classmethod
    def _get_or_create(cls, model_class, *args, **kwargs):
        address = kwargs.pop('address', 'a@b.com')
        sub = super()._get_or_create(model_class, *args, **kwargs)
        AddressAssignmentFactory(channel=sub.channel,
                                 user=sub.subscriber,
                                 address=AddressFactory(user=sub.subscriber,
                                                        address=address))

        return sub


class AddressFactory(AutoRegisterModelFactory):
    class Meta:
        model = models.Address
        django_get_or_create = ('user', 'label')

    user = factory.SubFactory(UserFactory)
    label = factory.Sequence(lambda n: 'Label %03d' % n)
    address = factory.Sequence(lambda n: 'Address %03d' % n)


class AddressAssignmentFactory(AutoRegisterModelFactory):
    class Meta:
        model = models.AddressAssignment
        django_get_or_create = ('user', 'channel')

    user = factory.SubFactory(UserFactory)
    address = factory.SubFactory(AddressFactory)
    channel = factory.SubFactory(ChannelFactory)
