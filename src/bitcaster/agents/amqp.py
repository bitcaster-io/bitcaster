from typing import TYPE_CHECKING, Any

import contextlib
import json
import logging

import pika

from django import forms
from django.utils.translation import gettext_lazy as _

from bitcaster.models import Event

from .base import Agent, AgentConfig

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel

logger = logging.getLogger(__name__)


class AMQPConfig(AgentConfig):
    host = forms.CharField(label=_("Host"), help_text=_("RabbitMQ server hostname"))
    port = forms.IntegerField(label=_("Port"), initial=5672, help_text=_("RabbitMQ server port"))
    virtual_host = forms.CharField(label=_("Virtual Host"), initial="/", required=False)
    username = forms.CharField(label=_("Username"), help_text=_("RabbitMQ username"))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput, help_text=_("RabbitMQ password"))
    queue = forms.CharField(label=_("Queue"), help_text=_("Queue name to consume from"))
    exchange = forms.CharField(label=_("Exchange"), required=False, help_text=_("Exchange name (optional)"))
    routing_key = forms.CharField(label=_("Routing Key"), required=False, help_text=_("Routing key (optional)"))
    prefetch_count = forms.IntegerField(
        label=_("Prefetch Count"), initial=1, required=False, help_text=_("QoS prefetch count")
    )
    event_field = forms.CharField(
        label=_("Event Field"),
        initial="event",
        required=False,
        help_text=_("JSON field name that holds the event slug"),
    )
    max_messages = forms.IntegerField(
        label=_("Max Messages"),
        initial=10,
        required=False,
        help_text=_("Maximum messages to consume per check cycle"),
    )


class AgentAMQP(Agent):
    config_class: type[AMQPConfig] = AMQPConfig
    verbose_name = "RabbitMQ"

    @property
    def cfg(self) -> dict[str, Any]:
        return {
            "host": self.config["host"],
            "port": self.config.get("port", 5672),
            "virtual_host": self.config.get("virtual_host") or "/",
            "username": self.config["username"],
            "password": self.config["password"],
            "queue": self.config["queue"],
            "exchange": self.config.get("exchange") or "",
            "routing_key": self.config.get("routing_key") or "",
            "prefetch_count": self.config.get("prefetch_count") or 1,
            "event_field": self.config.get("event_field") or "event",
            "max_messages": self.config.get("max_messages") or 10,
        }

    def get_connection_params(self) -> pika.ConnectionParameters:
        c = self.cfg
        credentials = pika.PlainCredentials(c["username"], c["password"])
        return pika.ConnectionParameters(
            host=c["host"],
            port=c["port"],
            virtual_host=c["virtual_host"],
            credentials=credentials,
        )

    def ensure_queue(self, channel: "BlockingChannel") -> None:
        c = self.cfg
        if c["exchange"]:
            channel.queue_declare(queue=c["queue"], durable=True)
            channel.queue_bind(queue=c["queue"], exchange=c["exchange"], routing_key=c["routing_key"])
        else:
            channel.queue_declare(queue=c["queue"], durable=True)

    def consume_messages(self, channel: "BlockingChannel") -> list[tuple[Any, Any, bytes]]:
        messages: list[tuple[Any, Any, bytes]] = []
        max_msgs = self.cfg["max_messages"]
        for method_frame, properties, body in channel.consume(self.cfg["queue"], inactivity_timeout=1.0):
            if method_frame is None:
                break
            messages.append((method_frame, properties, body))
            if len(messages) >= max_msgs:
                break
        return messages

    def process_message(self, body: bytes) -> bool:
        try:
            msg: dict[str, Any] = json.loads(body)
        except json.JSONDecodeError as e:
            logger.error("Failed to decode message: %s", e)
            return False

        event_field = self.cfg["event_field"]
        event_slug: Any = msg.get(event_field)
        if not event_slug:
            logger.warning("Message missing event field '%s'", event_field)
            return False

        try:
            event: Event = Event.objects.get(
                slug=str(event_slug),
                application=self.monitor.event.application_id,
            )
        except Event.DoesNotExist:
            logger.warning("Event '%s' not found", event_slug)
            return False

        context: dict[str, Any] = msg.get("data", {})
        try:
            event.trigger(context=context)
            return True
        except Exception:
            logger.exception("Failed to trigger event '%s'", event_slug)
            return False

    def check(self, notify: bool = True, update: bool = True) -> None:
        try:
            connection = pika.BlockingConnection(self.get_connection_params())
        except Exception:
            logger.exception("Failed to connect to RabbitMQ")
            return
        try:
            try:
                channel = connection.channel()
            except Exception:
                logger.exception("Failed to open channel")
                return
            channel.basic_qos(prefetch_count=self.cfg["prefetch_count"])
            self.ensure_queue(channel)
            messages = self.consume_messages(channel)
            for method_frame, _properties, body in messages:
                try:
                    if self.process_message(body):
                        channel.basic_ack(method_frame.delivery_tag)
                    else:
                        channel.basic_nack(method_frame.delivery_tag, requeue=False)
                except Exception:
                    logger.exception("Error processing message")
                    channel.basic_nack(method_frame.delivery_tag, requeue=False)
            channel.cancel()
        finally:
            with contextlib.suppress(Exception):
                connection.close()

    def changes_detected(self) -> bool:
        connection = pika.BlockingConnection(self.get_connection_params())
        try:
            channel = connection.channel()
            self.ensure_queue(channel)
            method_frame, _properties, _body = channel.basic_get(self.cfg["queue"])
            if method_frame:
                channel.basic_nack(method_frame.delivery_tag, requeue=True)
                return True
            return False
        finally:
            with contextlib.suppress(Exception):
                connection.close()

    def notify(self) -> None:
        self.check(notify=True, update=False)
