from django.db.models import Model

from . import base

# from . import base
from .address import AddressFactory  # noqa
from .assignment import AssignmentFactory  # noqa
from .browser import BrowserFactory  # noqa
from .channel import ChannelFactory  # noqa
from .distribution import DistributionListFactory  # noqa
from .django_auth import GroupFactory, PermissionFactory  # noqa
from .django_celery_beat import PeriodicTaskFactory  # noqa
from .event import EventFactory  # noqa
from .key import ApiKeyFactory  # noqa
from .log import LogEntryFactory  # noqa
from .media import MediaFileFactory  # noqa
from .message import MessageFactory  # noqa
from .notification import NotificationFactory  # noqa
from .occurrence import OccurrenceFactory  # noqa
from .org import ApplicationFactory, OrganizationFactory, ProjectFactory  # noqa
from .social import SocialProviderFactory  # noqa
from .user import SuperUserFactory, UserFactory  # noqa
from .userrole import UserRoleFactory  # noqa


def get_factory_for_model(_model: Model) -> type[base.TAutoRegisterModelFactory]:
    class Meta:
        model = _model

    bases = (base.AutoRegisterModelFactory,)
    if _model in base.factories_registry:
        return base.factories_registry[_model]  # noqa

    return type(f"{_model._meta.model_name}AutoCreatedFactory", bases, {"Meta": Meta})  # noqa
