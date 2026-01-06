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

        # Ensure the user has an email, otherwise we can't create a group name
        if not self.user.email:
            logger.error(f"User {self.user.username} has no email, cannot join chat group.")
            await self.close(code=4003)
            return

        self.email = self.user.email # Use the authenticated user's email
        self.username = self.user.username

        # The email must be encoded to create a safe group name
        safe_email = base64.urlsafe_b64encode(self.email.encode()).decode()
        self.group_name = f"chrome_chat_{safe_email}" # Changed group name for clarity and distinction

        logger.info(f"Accepting chat connection for '{self.email}' ({self.username}) and adding to group '{self.group_name}'")

        # Join room group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        logger.info(f"Disconnecting '{self.email}' ({self.username}) from group '{self.group_name}'")
        # Leave room group
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """Receive message from WebSocket."""
        data = json.loads(text_data)
        message = data.get("message")

        if message:
            logger.info(f"Received message from {self.username} in group {self.group_name}: {message}")
            # Send message to room group
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat_message", # Custom type for chat messages
                    "message": message,
                    "username": self.username,
                }
            )
        else:
            logger.warning(f"Received empty or invalid message from {self.username} in group {self.group_name}.")

    async def chat_message(self, event):
        """Receive message from room group (channels layer) and send to WebSocket."""
        message = event["message"]
        username = event["username"]

        # Send message to WebSocket client
        await self.send(
            text_data=json.dumps(
                {
                    "event": "chat_message", # Distinguish from chrome_message
                    "message": message,
                    "username": username,
                }
            )
        )

    # Renamed the original method to avoid confusion and make it clear it's for dispatcher messages
    async def chrome_plugin_message(self, event):
        """Send messages from the backend dispatcher to the WebSocket client (original functionality)."""
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
