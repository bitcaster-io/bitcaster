from django.db.models import Model

from . import base
from .address import AddressFactory
from .assignment import AssignmentFactory
from .attachment import AttachmentFactory
from .browser import BrowserFactory
from .channel import ChannelFactory
from .client_token import ClientTokenFactory
from .delivery import DeliveryFactory
from .deliverysimulation import DeliverySimulationFactory
from .distribution import DistributionListFactory
from .django_auth import GroupFactory, PermissionFactory
from .event import EventFactory
from .eventsimulation import EventSimulationFactory
from .internal import LogMessageFactory
from .key import ApiKeyFactory
from .log import LogEntryFactory
from .media import MediaFileFactory
from .member import MemberFactory
from .membership import ApplicationMembershipFactory
from .message import MessageTemplateFactory
from .monitor import MonitorFactory
from .notification import NotificationFactory
from .occurrence import OccurrenceFactory
from .org import ApplicationFactory, OrganizationFactory, ProjectFactory
from .processlog import ProcessLogEntryFactory
from .social import SocialAccountFactory, SocialProviderFactory
from .subscription import SubscriptionFactory
from .task import TaskFactory
from .user import SuperUserFactory, UserFactory
from .usermessage import UserMessageFactory
from .userrole import UserRoleFactory

__all__ = [
    "AddressFactory",
    "ApiKeyFactory",
    "ApplicationFactory",
    "ApplicationMembershipFactory",
    "AssignmentFactory",
    "AttachmentFactory",
    "BrowserFactory",
    "BrowserFactory",
    "ChannelFactory",
    "ClientTokenFactory",
    "DeliveryFactory",
    "DeliverySimulationFactory",
    "DistributionListFactory",
    "EventFactory",
    "EventSimulationFactory",
    "GroupFactory",
    "GroupFactory",
    "LogEntryFactory",
    "LogMessageFactory",
    "MediaFileFactory",
    "MemberFactory",
    "MessageTemplateFactory",
    "MonitorFactory",
    "NotificationFactory",
    "OccurrenceFactory",
    "OrganizationFactory",
    "PermissionFactory",
    "ProjectFactory",
    "ProjectFactory",
    "ProcessLogEntryFactory",
    "SocialAccountFactory",
    "SocialProviderFactory",
    "SubscriptionFactory",
    "SuperUserFactory",
    "TaskFactory",
    "UserFactory",
    "UserMessageFactory",
    "UserRoleFactory",
]


def get_factory_for_model(_model: Model) -> "type[base.TAutoRegisterModelFactory]":
    class Meta:
        model = _model

    bases = (base.AutoRegisterModelFactory,)
    if _model in base.factories_registry:
        return base.factories_registry[_model]

    return type(f"{_model._meta.model_name}AutoCreatedFactory", bases, {"Meta": Meta})
