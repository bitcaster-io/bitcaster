# RabbitMQ Dispatcher

The RabbitMQ dispatcher publishes notification payloads to a RabbitMQ
exchange, so external consumers can receive them through the AMQP protocol.

## Configuration

The following parameters are required to configure the RabbitMQ dispatcher:

- **Host**: the RabbitMQ server hostname (default `localhost`).
- **Port**: the RabbitMQ server port (default `5672`).
- **Username**: the AMQP username (default `guest`).
- **Password**: the AMQP password (default `guest`).
- **Virtual Host**: the AMQP virtual host (default `/`).
- **Exchange**: the exchange to publish to (default `bitcaster`).
- **Exchange Type**: the exchange type — `Direct`, `Topic`, `Fanout` or
  `Headers` (default `Topic`).
- **Routing Key**: the routing key used to publish. If empty, the event slug
  is used.

## How to use

1. Select `RabbitMQ` as dispatcher for a Channel.
2. Fill the form with the connection parameters to your RabbitMQ server and
   the exchange to publish to.
3. Save the Channel.

Now you can add this channel to your Application and send notifications.
Consumers listening on the configured exchange and routing key receive a JSON
message with the full delivery payload plus the `event` field containing the
event slug.
