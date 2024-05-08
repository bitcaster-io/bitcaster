from . import base
from .address import Address, AddressFactory  # noqa
from .channel import Channel, ChannelFactory  # noqa
from .distribution import DistributionList, DistributionListFactory  # noqa
from .django_auth import Group, GroupFactory, Permission, PermissionFactory  # noqa
from .django_celery_beat import PeriodicTask, PeriodicTaskFactory  # noqa
from .event import Event, EventFactory  # noqa
from .key import ApiKey, ApiKeyFactory  # noqa
from .log import LogEntryFactory, LogMessage  # noqa
from .media import MediaFile, MediaFileFactory  # noqa
from .message import Message, MessageFactory  # noqa
from .notification import Notification, NotificationFactory  # noqa
from .occurrence import Occurrence, OccurrenceFactory  # noqa
from .org import ApplicationFactory, OrganizationFactory, ProjectFactory  # noqa
from .social import SocialProvider, SocialProviderFactory  # noqa
from .user import SuperUserFactory, User, UserFactory  # noqa
from .userrole import UserRole, UserRoleFactory  # noqa
from .validation import Validation, ValidationFactory  # noqa


def get_factory_for_model(_model) -> type[base.TAutoRegisterModelFactory]:
    class Meta:
        model = _model

    bases = (base.AutoRegisterModelFactory,)
    if _model in base.factories_registry:
        return base.factories_registry[_model]  # noqa

    return type(f"{_model._meta.model_name}AutoCreatedFactory", bases, {"Meta": Meta})  # noqa
