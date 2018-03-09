# -*- coding: utf-8 -*-

import pytz
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import JSONField
from strategy_field.contrib.drf import DrfStrategyField
from strategy_field.utils import import_by_name

from bitcaster import logging
from bitcaster.dispatchers import dispatcher_registry
from bitcaster.models import Application, Channel, Event, User
from bitcaster.models.message import Message
from bitcaster.models.subscription import Subscription

logger = logging.getLogger(__name__)


class TimezoneField(serializers.Field):
    def to_representation(self, obj):
        return str(obj)

    def to_internal_value(self, data):
        try:
            return pytz.timezone(str(data))
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValidationError('Unknown timezone')


class PasswordSerializer(serializers.Serializer):
    password1 = serializers.CharField()
    password2 = serializers.CharField()

    def validate(self, attrs):
        if attrs.get('password1', None) != attrs.get('password2', None):
            raise ValidationError('Passwords do not match')
        return attrs


# class RegisterUserSerializer(serializers.ModelSerializer):
#     first_name = serializers.CharField(required=True)
#     last_name = serializers.CharField(required=True)
#     email = serializers.EmailField(required=True)
#
#     class Meta:
#         model = User
#         fields = ('last_name', 'first_name', 'email')
#
#     def validate(self, attrs):
#         attrs['username'] = attrs.get('email', '')
#         return super(RegisterUserSerializer, self).validate(attrs)


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField()
    password2 = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('id', 'last_name', 'first_name', 'email',
                  'password2', 'password',)
        write_only_fields = ('password', 'password2')
        read_only_fields = ('id',)

        def validate(self, attrs):
            if attrs.get('password', None) != attrs.get('password2', None):
                raise ValidationError('Passwords do not match')
            attrs.pop('password2')
            return attrs


class UserSerializer(serializers.ModelSerializer):
    timezone = TimezoneField(default='UTC')

    class Meta:
        model = User
        fields = ['name', 'email', 'id',
                  'timezone', 'language',
                  ]
        read_only_fields = ['id', ]

    def validate_password(self, value):
        return make_password(value)


class UserSerializerLight(UserSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email']


# class MaintainerSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(required=True)
#
#     class Meta:
#         model = User
#         fields = ('email',)
#         read_only_fields = ('email',)
#
#     def validate_email(self, value):
#         if not User.objects.filter(email=value).exists():
#             raise ValidationError("Invalid user")
#         return value


class ApplicationSerializer(serializers.ModelSerializer):
    timezone = TimezoneField(default='UTC')
    owner = UserSerializerLight(read_only=True)
    # maintainers = serializers.PrimaryKeyRelatedField(many=True,
    #                                                  queryset=User.objects.all(),
    #                                                  required=False)

    class Meta:
        model = Application
        read_only_fields = ('token', 'owner')
        write_only_fields = ('password',)
        exclude = []

    def save(self, **kwargs):
        self.validated_data['owner'] = self.context['request'].user
        return super().save(**kwargs)


class ApplicationNestedMixin(object):
    def __init__(self, *args, **kwargs):
        pk = kwargs['context']['view'].kwargs.get('application__pk', None)
        self.application = Application.objects.get(pk=pk)
        super().__init__(*args, **kwargs)

    def save(self, **kwargs):
        self.validated_data['application'] = self.application
        return super().save(**kwargs)


class ChannelSerializer(ApplicationNestedMixin, serializers.ModelSerializer):
    application_name = serializers.StringRelatedField(source='application.name',
                                                      read_only=True)

    handler = DrfStrategyField(dispatcher_registry, required=True)
    config = JSONField(required=True)

    # def validate_handler(self, value):
    #     try:
    #         if not dispatcher_registry.is_valid(value):
    #             raise ValidationError
    #     except:
    #         valid = sorted(fqn(klass) for klass in dispatcher_registry)
    #         raise ValidationError("Invalid dispatcher '{}'. Valid values are: {}".format(value, valid))
    #
    #     return value
    #
    def validate(self, attrs):
        if 'handler' in attrs:
            handler = import_by_name(attrs['handler'])(self)
        else:
            handler = self.instance.handler
        if handler:
            config = attrs.get('config', {})
            try:
                handler.validate_configuration(config, True)
            except ValidationError as e:
                raise ValidationError({"config": [e.detail]})
        return super().validate(attrs)

    class Meta:
        model = Channel
        exclude = ()
        # fields = ('application', 'name', 'handler', 'config', 'id',
        #           'application_name')
        read_only_fields = ('id',)


#
# class MonitorSerializer(ApplicationNestedMixin, serializers.ModelSerializer):
#     application_name = serializers.StringRelatedField(source='application.name',
#                                                       read_only=True)
#
#     handler = DrfStrategyField(monitor_registry, required=True)
#     config = JSONField(required=False)
#
#     class Meta:
#         model = Monitor
#         fields = ('application', 'application_name',
#                   'name', 'handler', 'config', 'id', 'event')
#         read_only_fields = ('id', 'application')
#
#     # def __init__(self, instance=None, *, application=None, **kwargs):
#     #     self.application = application
#     #     super().__init__(instance, **kwargs)
#     #
#     # def validate_handler(self, value):
#     #     try:
#     #         if not monitor_registry.is_valid(value):
#     #             raise ValidationError
#     #     except:
#     #         valid = sorted(fqn(klass) for klass in dispatcher_registry)
#     #         raise ValidationError("Invalid dispatcher '{}'. Valid values are: {}".format(value, valid))
#     #
#     #     return value
#
#     def validate(self, attrs):
#         if 'handler' in attrs:
#             handler = import_by_name(attrs['handler'])
#         else:
#             handler = self.instance.handler
#
#         if handler:
#             config = attrs.get('config', {})
#             valid, errors = handler.validate(config)
#             if not valid:
#                 raise ValidationError({"config": [errors]})
#
#         if self.application != attrs['event'].application:
#             raise ValidationError("Invalid event")
#
#         return super().validate(attrs)


class EventSerializer(ApplicationNestedMixin, serializers.ModelSerializer):
    preferences = JSONField(required=False)

    class Meta:
        model = Event
        fields = ('name', 'id', 'preferences')
        read_only_fields = ('id',)


class MessageSerializer(ApplicationNestedMixin, serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('event', 'channels', 'application',
                  'subject', 'body', 'id', 'name')
        read_only_fields = ('id', 'application')

    def __init__(self, instance=None, *args, **kwargs):
        super().__init__(instance, **kwargs)
        self.fields['channels'].queryset = self.application.channels.all()


class SubscriptionSerializer(serializers.ModelSerializer):
    subscriber = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Subscription
        fields = ('channel', 'subscriber', 'event', 'active', 'id', 'config')
        read_only_fields = ('id',)

    def __init__(self, *args, **kwargs):
        pk = kwargs['context']['view'].kwargs.get('user__pk', None)
        self.user = User.objects.get(pk=pk)
        super().__init__(*args, **kwargs)

    def save(self, **kwargs):
        self.validated_data['subscriber'] = self.user
        return super().save(**kwargs)

    def validate(self, attrs):
        channel = attrs.get('channel', None)
        event = attrs.get('event', None)
        if channel and event:
            if not channel.messages.filter(event=event).exists():
                raise ValidationError('Channel cannot be used as no messages are configured for it')
        return super().validate(attrs)
