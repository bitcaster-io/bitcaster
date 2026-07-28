from typing import TYPE_CHECKING, Any

import json
import logging

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import BasicProperties

from django import forms
from django.utils.translation import gettext_lazy as _

from bitcaster.dispatchers.base import Dispatcher, DispatcherConfig, MessageProtocol, Payload
from bitcaster.exceptions import DispatcherError

if TYPE_CHECKING:
    from bitcaster.models import Assignment

logger = logging.getLogger(__name__)


class RabbitMQConfig(DispatcherConfig):
    host = forms.CharField(label=_("Host"), initial="localhost", help_text=_("RabbitMQ server hostname."))
    port = forms.IntegerField(label=_("Port"), initial=5672, help_text=_("RabbitMQ server port."))
    username = forms.CharField(label=_("Username"), initial="guest", required=False, help_text=_("AMQP username."))
    password = forms.CharField(
        label=_("Password"),
        initial="guest",
        required=False,
        widget=forms.PasswordInput(render_value=True),
        help_text=_("AMQP password."),
    )
    vhost = forms.CharField(label=_("Virtual Host"), initial="/", required=False, help_text=_("AMQP virtual host."))
    exchange = forms.CharField(label=_("Exchange"), initial="bitcaster", help_text=_("Exchange name."))
    exchange_type = forms.ChoiceField(
        label=_("Exchange Type"),
        choices=lambda: [("direct", "Direct"), ("topic", "Topic"), ("fanout", "Fanout"), ("headers", "Headers")],
        initial="topic",
    )
    routing_key = forms.CharField(
        label=_("Routing Key"),
        required=False,
        help_text=_("Routing key (defaults to event slug if empty)."),
    )


class RabbitMQDispatcher(Dispatcher):
    slug = "rabbitmq"
    verbose_name = "RabbitMQ"
    protocol = MessageProtocol.PLAINTEXT
    config_class = RabbitMQConfig

    def _get_connection_params(self) -> dict[str, Any]:
        return {
            "host": self.config["host"],
            "port": self.config["port"],
            "credentials": pika.PlainCredentials(
                self.config.get("username", "guest"),
                self.config.get("password", "guest"),
            ),
            "virtual_host": self.config.get("vhost", "/"),
        }

    def _get_channel(self) -> BlockingChannel:
        conn = pika.BlockingConnection(pika.ConnectionParameters(**self._get_connection_params()))
        channel = conn.channel()
        channel.exchange_declare(
            exchange=self.config["exchange"],
            exchange_type=self.config["exchange_type"],
            durable=True,
        )
        return channel

    def _send(self, address: str, payload: Payload, assignment: "Assignment | None" = None, **kwargs: Any) -> bool:
        try:
            channel = self._get_channel()
            routing_key = self.config.get("routing_key") or payload.event.slug
            body = payload.as_dict()
            body["event"] = payload.event.slug
            channel.basic_publish(
                exchange=self.config["exchange"],
                routing_key=routing_key,
                body=json.dumps(body),
                properties=BasicProperties(delivery_mode=2),
            )
            channel.connection.close()
            return True
        except Exception as e:
            raise DispatcherError(f"RabbitMQ publish failed: {e}") from e
