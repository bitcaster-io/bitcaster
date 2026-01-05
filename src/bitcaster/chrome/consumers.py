import base64
import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class ChromeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            logger.warning("Rejecting anonymous connection for WebSocket")
            await self.close(code=4003)
            return

        self.email = self.scope["url_route"]["kwargs"]["email"]

        # The email must be encoded to create a safe group name that matches the dispatcher
        safe_email = base64.urlsafe_b64encode(self.email.encode()).decode()
        self.group_name = f"chrome_{safe_email}"

        logger.info(f"Accepting connection for '{self.email}' and adding to group '{self.group_name}'")

        # Join room group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        logger.info(f"Disconnecting '{self.email}' from group '{self.group_name}'")
        # Leave room group
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def chrome_message(self, event):
        """Send messages from the backend dispatcher to the WebSocket client."""
        logger.debug(f"Sending event '{event['event']}' to client {self.email}")
        # Send message to WebSocket client
        await self.send(
            text_data=json.dumps(
                {
                    "event": event["event"],
                    "data": event["data"],
                }
            )
        )
